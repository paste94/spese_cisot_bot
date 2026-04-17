from functools import wraps
import traceback
import logging

from config import DIV_STRINGS

logger = logging.getLogger(__name__)

def handle_errors(bot):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log completo stacktrace
                error_msg = f"❌ ERRORE in {func.__name__}:\n{str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                
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
    return decorator

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

class MessageFormatNotSupported(Exception):
    """Errore conversione float personalizzato"""
    pass