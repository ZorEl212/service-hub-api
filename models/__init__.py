from models.engine.db_storage import DBStorage
from models.engine.media_storage import MediaStorage
from services.elastic import ElasticSearchConfig

storage = DBStorage()
media_storage = MediaStorage()
es = ElasticSearchConfig()

from models.engine.auth import AuthEngine as VerificationAuth, AuthEngine
from models.engine.email_client import EmailClient

email_client = EmailClient()
from models.auth import Auth

auth = Auth()
sms_auth = AuthEngine()


