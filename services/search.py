from traceback import print_exc
from typing import List, Optional, Set

from beanie import PydanticObjectId

import models
from models.attributes import ALLOWED_SUBCATEGORIES, Subcategory
from models.service import ServiceItem
from models.service_provider import ServiceProvider
from schemas.generic_schemas import SearchFilters
from utils.exceptions import AppException
from utils.service_result import ServiceResult


class SearchEngine:
    async def format_provider(self, provider: ServiceProvider) -> dict:
        initials = "".join(word[0] for word in provider.name.split()[:2]).upper()

        price_str, price_range = await provider.get_price_range()
        #available_now = is_provider_available_now(provider)

        return {
            "id": str(provider.id),
            "title": provider.name,
            "provider": provider.name,
            "providerInitials": initials,
            "description": provider.description or "",
            "rating": provider.averageRating or 0.0,
            "reviews": provider.reviewCount or 0,
            "image": provider.image if hasattr(provider, "image_url") else "/placeholder.svg?height=200&width=300",
            "price": price_str,
            "priceRange": price_range,
            "location": provider.address.city if provider.address else "Unknown",
            "categories": list(provider.category.values()) if provider.category else [],
            "mainCategory": (
                list(provider.category.keys())[0]
                if hasattr(provider, "category") and isinstance(provider.category, dict) and provider.category
                else "General"
            ),
            "availableNow": True
        }

    async def search(self, filters: SearchFilters) -> ServiceResult:
        try:
            candidate_provider_ids: Optional[Set[PydanticObjectId]] = None
            id_selection_filter_applied = False
            providers: List[ServiceProvider] = []

            if filters.q or filters.category:
                sub_categories = ALLOWED_SUBCATEGORIES.get(filters.category, [])
                if filters.subcategory:
                    sub_categories = [filters.subcategory]
                es_ids = await models.es.search_providers(filters.q, filters.category, sub_categories)
                candidate_provider_ids = set(PydanticObjectId(id) for id in es_ids)
                id_selection_filter_applied = True
                if not candidate_provider_ids:
                    return self._empty_result(filters)

            service_item_filter = {}
            if filters.price_min is not None:
                id_selection_filter_applied = True
                service_item_filter.setdefault("price", {})["$gte"] = filters.price_min
            if filters.price_max is not None:
                id_selection_filter_applied = True
                service_item_filter.setdefault("price", {})["$lte"] = filters.price_max

            if service_item_filter:
                service_items = await ServiceItem.find(service_item_filter, fetch_links=True).to_list()
                provider_ids_from_services = {PydanticObjectId(s.provider_id.id) for s in service_items}
                if candidate_provider_ids is not None:
                    candidate_provider_ids.intersection_update(provider_ids_from_services)
                    if not candidate_provider_ids:
                        return self._empty_result(filters)
                else:
                    candidate_provider_ids = provider_ids_from_services
                    if not candidate_provider_ids:
                        return self._empty_result(filters)

            provider_filter = {}
            if candidate_provider_ids is not None:
                provider_filter["_id"] = {"$in": list(candidate_provider_ids)}
            elif id_selection_filter_applied:
                return self._empty_result(filters)

            if filters.rating is not None and filters.rating > 0.0:
                provider_filter["averageRating"] = {"$gte": filters.rating}

            sort_order = self._get_sort_order(filters.sort, fallback=not id_selection_filter_applied)
            skip = (filters.page - 1) * filters.limit

            if filters.location:
                try:
                    long, lat = map(float, filters.location.split(","))
                    geo_near_stage = {
                        "$geoNear": {
                            "near": {
                                "type": "Point",
                                "coordinates": [long, lat]
                            },
                            "distanceField": "distance",
                            "spherical": True,
                            "query": provider_filter
                        }
                    }

                    # Only add maxDistance if filters.distance is set and > 100
                    if filters.distance and filters.distance > 100:
                        geo_near_stage["$geoNear"]["maxDistance"] = filters.distance

                    geo_pipeline = [
                        geo_near_stage,
                        {"$sort": dict(sort_order)},
                        {"$skip": skip},
                        {"$limit": filters.limit}
                    ]
                    raw_results = await ServiceProvider.get_motor_collection().aggregate(geo_pipeline).to_list(length=None)
                    total = len(raw_results)
                    providers = [ServiceProvider.model_validate(doc) for doc in raw_results]
                except ValueError:
                    # Invalid long/lat
                    print_exc()
                    return ServiceResult(AppException.GetItem())
            else:
                # Fallback: standard query
                providers, total = await models.storage.find_with_count(
                    cls=ServiceProvider,
                    filter_=provider_filter,
                    sort=sort_order,
                    skip=skip,
                    limit=filters.limit,
                    fetch_links=False
                )

            return ServiceResult({
                "page": filters.page,
                "limit": filters.limit,
                "total": total,
                "providers": [await self.format_provider(p) for p in providers]
            })

        except Exception:
            print_exc()
            return ServiceResult(AppException.GetItem())

    def _empty_result(self, filters: SearchFilters) -> ServiceResult:
        return ServiceResult({
            "page": filters.page,
            "limit": filters.limit,
            "total": 0,
            "providers": []
        })

    def _get_sort_order(self, sort: str, fallback: bool = False) -> List:
        if sort == "relevance" and not fallback:
            return [("created_at", -1)]
        elif sort == "rating":
            return [("rating", -1)]
        elif sort == "views":
            return [("reviewCount", -1)]
        else:
            return [("rating", -1), ("reviewCount", -1)]  # fallback for empty search