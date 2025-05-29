from beanie.odm.operators.update.general import Set


from models.message import Message, MessageAttachment
from models.user import User
from utils.exceptions import AppException
from utils.result import Result


from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId, DBRef
from beanie import PydanticObjectId
from fastapi import WebSocket
from traceback import print_exc


import models


class SocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, List[str]] = {}
        self.db = models.storage

    async def connect(self, sid: str, user_id: str, websocket: WebSocket):
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(sid)

        self.active_connections[sid] = websocket

    async def disconnect(self, sid: str):
        if sid in self.active_connections:
            print(sid)
            del self.active_connections[sid]

        for user_id, connections in self.user_connections.items():
            if sid in connections:
                connections.remove(sid)
                if not connections:
                    del self.user_connections[user_id]
                break

    def serialize_document(self, doc):
        if isinstance(doc, list):
            return [self.serialize_document(item) for item in doc]
        elif isinstance(doc, dict):
            return {k: self.serialize_document(v) for k, v in doc.items()}
        elif isinstance(doc, (ObjectId, PydanticObjectId)):
            return str(doc)
        elif isinstance(doc, datetime):
            return doc.isoformat()
        elif isinstance(doc, DBRef):
            return str(doc.id)
        return doc

    def serialize_user(self, user: User) -> dict:
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
        }

    async def serialize_message(self, message) -> dict:
        await message.fetch_all_links()
        result = {
            "id": str(message.id),
            "created_at": message.created_at.isoformat() if isinstance(message.created_at, datetime) else message.created_at,
            "updated_at": message.updated_at.isoformat() if isinstance(message.updated_at, datetime) else message.updated_at,
            "sender_id": str(getattr(message.sender_id, 'id', message.sender_id.id)),
            "receiver_id": str(getattr(message.receiver_id, 'id', message.receiver_id)),
            "content": message.content,
            "attachments": message.attachments,
            "read": message.read,
            "read_at": message.read_at.isoformat() if isinstance(message.read_at, datetime) else message.read_at,
        }
        return result

    async def serialize_messages(self, messages: List) -> List[dict]:
        return [await self.serialize_message(message) for message in messages]

    async def send_message(self, sender_id: User, receiver_id: str, content: str, attachments: Optional[List[dict]] = None) -> Result:
        try:
            receiver = await self.db.get(User, PydanticObjectId(receiver_id))
            if not receiver:
                return Result.failure(AppException("Receiver not found"))

            message = Message(
                sender_id=sender_id,
                receiver_id=receiver,
                content=content,
                attachments=[MessageAttachment(**a) for a in (attachments or [])],
                created_at=datetime.utcnow(),
            )
            await message.save()

            if receiver_id in self.user_connections:
                message_data = {"type": "new_message", "data": await message.to_read_model()}
                for sid in self.user_connections[receiver_id]:
                    if sid in self.active_connections:
                        await self.active_connections[sid].send_json(message_data)

            return Result.success(message)

        except Exception as e:
            return Result.failure(AppException(str(e)))

    async def mark_messages_read(self, user_id: User, sender_id: str) -> Result:
        try:
            updated_result = await Message.find(
                {
                    "sender_id.$id": PydanticObjectId(sender_id),
                    "receiver_id.$id": PydanticObjectId(user_id.id),
                    "read": False
                }
            ).update(
                Set({"read": True, "read_at": datetime.utcnow()})
            )

            if updated_result.modified_count > 0 and sender_id in self.user_connections:
                notification = {"type": "messages_read", "data": {"user_id": str(user_id.id)}}
                for sid in self.user_connections[sender_id]:
                    if sid in self.active_connections:
                        await self.active_connections[sid].send_json(notification)
                        print("Sent read notification to", sid)


            return Result.success(updated_result.modified_count)

        except Exception as e:
            return Result.failure(AppException(str(e)))

    async def get_chat_rooms(self, user_id: User) -> Result:
        try:
            user_oid = PydanticObjectId(user_id.id)
            pipeline = [
                {"$match": {"$or": [
                    {"sender_id.$id": user_oid},
                    {"receiver_id.$id": user_oid}
                ]}},
                {"$group": {
                    "_id": {"$cond": [
                        {"$eq": ["$sender_id.$id", user_oid]},
                        "$receiver_id.$id",
                        "$sender_id.$id"
                    ]},
                    "last_message": {"$last": "$$ROOT"},
                    "unread_count": {"$sum": {"$cond": [
                        {"$and": [
                            {"$eq": ["$receiver_id.$id", user_oid]},
                            {"$eq": ["$read", False]}
                        ]}, 1, 0
                    ]}}
                }},
                {"$lookup": {
                    "from": "User",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "user"
                }},
                {"$unwind": "$user"},
                {"$project": {
                    "user": {"id": "$user._id", "email": "$user.email", "role": "$user.role"},
                    "last_message": 1,
                    "unread_count": 1
                }}
            ]

            chat_rooms = await Message.aggregate(pipeline).to_list(None)
            return Result.success(self.serialize_document(chat_rooms))

        except Exception as e:
            print_exc()
            return Result.failure(AppException(str(e)))

    async def get_chat_history(self, user_id: User, other_user_id: str, page: int = 1, limit: int = 50) -> Result:
        try:
            user_oid = PydanticObjectId(user_id.id)
            other_oid = PydanticObjectId(other_user_id)
            skip = (page - 1) * limit

            query = {"$or": [
                {"sender_id.$id": user_oid, "receiver_id.$id": other_oid},
                {"sender_id.$id": other_oid, "receiver_id.$id": user_oid},
            ]}

            messages = (await Message.find(query)
                        .sort("-created_at")
                        .skip(skip)
                        .limit(limit)
                        .to_list())

            total = await Message.find(query).count()
            serialized = await self.serialize_messages(messages)

            return Result.success({
                "messages": serialized[::-1],
                "total": total,
                "page": page,
                "limit": limit,
                "has_more": skip + len(messages) < total
            })

        except Exception as e:
            return Result.failure(AppException(str(e)))
