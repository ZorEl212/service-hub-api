from cgi import FieldStorage

import models
from models.engine.file_storage import FileStorage


class DBSessionContext(object):
    def __init__(self):
        self.db = models.storage
        self.media_storage = models.media_storage
        print(f"Storage instance: {type(self.db)}")

class AppCRUD(DBSessionContext):
    pass
