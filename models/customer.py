from beanie import Document, Link

from models.user import User


class Customer(Document):
    user_id: Link[User]
    first_name: str = ""
    last_name: str = ""
    username: str = ""

