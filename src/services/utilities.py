import time

from services.users.exceptions import UnauthorizedMessageError
from services.logger.logger import logger
from functools import wraps


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
                    t0 = time.time()
                    bot.send_message(chat_id, f"❌ Errore interno: {str(e)}")
                    t1 = time.time()
                    logger.info(
                        "📥 Messaggio ERRORE inoltrato | Ritardo invio: %.2fs",
                        t1-t0
                    )
            except:
                pass  # Se non riesce a mandare, ignora
            
            return None
    return wrapper

def send_upload_document_action(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        bot.send_chat_action(message.chat.id, "upload_document")
        return func(message, *args, **kwargs)
    return wrapper

