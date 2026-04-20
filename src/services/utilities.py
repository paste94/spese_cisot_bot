from telebot.types import User
from services.users.exceptions import UnauthorizedMessageError
from services.users.users import USERS
from services.logger.logger import logger
from functools import wraps

from config import DIV_STRINGS

from bot_instance import bot

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnauthorizedMessageError as e:
            logger.warning(
                "Accesso non autorizzato — user='%s' telegram_id=%s",
                e.user_name,
                e.telegram_id,
                exc_info=False # No stacktrace per accessi non autorizzati
            )

        except Exception as e:
            logger.error(
                "Errore in %s: %s",
                func.__qualname__,
                e,
                exc_info=True # Stacktrace completo
            )
            
            # Manda messaggio errore all'utente (se disponibile)
            try:
                logger.info("Invio messaggio di errore all'utente")
                if args and hasattr(args[0], 'chat'):
                    chat_id = args[0].chat.id
                    bot.send_message(chat_id, f"❌ Errore interno: {str(e)}")
            except:
                pass  # Se non riesce a mandare, ignora
            
            return None
    return wrapper

def check_user(user: User):
    if not USERS.is_authorized(user.username):
        raise UnauthorizedMessageError(user.username, user.id)

def parse_message(message):
    tokens = message.strip().split(' ', 1)
    try: 
        price = float(tokens[0].replace(',', '.'))
    except ValueError as e:
        if "could not convert string to float" in str(e):
            raise MessageFormatNotSupported(f"Impossibile convertire '{tokens[0].replace(',', '.')}' in numero. Il formato corretto è <NUMERO> <DESCRIZIONE> <Diviso?>") 

    try:
        if tokens[1].lower().endswith(tuple(DIV_STRINGS)):
            split = True
        else:
            split = False
        description = tokens[1].replace('diviso', '').replace(',','').strip()
    except ValueError as e:
        if "list index out of range" in str(e):
            raise MessageFormatNotSupported(f"Descriziona mancante. Il formato corretto è <NUMERO> <DESCRIZIONE> <Diviso?>") 

    row = {
        'price': price,
        'description': description,
        'split': split,
    }
    return row

def send_upload_document_action(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        bot.send_chat_action(message.chat.id, "upload_document")
        return func(message, *args, **kwargs)
    return wrapper

class MessageFormatNotSupported(Exception):
    """Errore conversione float personalizzato"""
    pass