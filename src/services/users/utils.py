from telebot.types import User
from services.users.users import USERS
from services.users.exceptions import UnauthorizedMessageError

def check_user(user: User):
    if not USERS.is_authorized(user.username):
        raise UnauthorizedMessageError(user.username, user.id)