from models.engine.db_storage import DBStorage
from services.elastic import ElasticSearchConfig

storage = DBStorage()
es = ElasticSearchConfig()

from models.auth import Auth

auth = Auth()
