from models.engine.db_storage import DBStorage
from models.engine.media_storage import MediaStorage
from services.elastic import ElasticSearchConfig

storage = DBStorage()
media_storage = MediaStorage()
es = ElasticSearchConfig()

from models.auth import Auth

auth = Auth()
