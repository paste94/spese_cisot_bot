import gspread
from config import SCOPES
from config import CREDENTIALS_FILE
from model.row import Row
import time
import logging

from gspread import NoValidUrlKeyFound
from config import MONTH_NAMES
from services.gsheet.exceptions import UnknownLinkError
from services.users.users import USERS
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Cache nomi sheet (TTL 5 minuti) ──────────────────────────
_sheet_name_cache: dict = {}   # url -> (name, timestamp)
_CACHE_TTL = 300               # secondi

def _create_gspread_client():
    client = gspread.service_account(
        filename=CREDENTIALS_FILE,
        scopes=SCOPES,
    )

    # 10 secondi per connettersi, 30 secondi per ricevere la risposta
    client.set_timeout((10, 30))

    # Evita di riutilizzare connessioni HTTP persistenti potenzialmente stale
    client.http_client.session.headers.update({
        "Connection": "close",
    })

    return client

def get_sheet_name(url: str) -> str:
    """Restituisce il titolo dello spreadsheet, con cache di 5 minuti."""
    now = time.time()

    # Controlla la cache
    if url in _sheet_name_cache:
        name, cached_at = _sheet_name_cache[url]
        if now - cached_at < _CACHE_TTL:
            return name

    try:
        client = _create_gspread_client()

        spreadsheet = client.open_by_url(url)
        name = spreadsheet.title
        _sheet_name_cache[url] = (name, now)
        return name
    except Exception as e:
        if isinstance(e, NoValidUrlKeyFound):
            raise UnknownLinkError("Link Google Sheet non valido")
        if isinstance(e, PermissionError):
            raise PermissionError(
                "Accesso negato allo Sheet. Per ottenerlo, accedere allo "
                "sheet e condividerlo con l'user del bot <code>sa-cisot-bot@eighth-brace-469407-e3.iam.gserviceaccount.com</code>."
            )
        raise e
    finally:
        if client is not None:
            client.http_client.session.close()
            
def add_row(row: Row, username: str):
    """Aggiunge una riga allo sheet usando solo 3 chiamate API (prima erano 7)."""
    try : 
        start = time.time()

        now = datetime.now()
        month = MONTH_NAMES[now.month]

        logger.debug("Creating client for user %s...", username)
        client = _create_gspread_client()
        logger.debug("User %s has been added to the client, time: [%.2fs]", username, time.time() - start)

        logger.debug("Getting sheet for user %s...", username)
        if row.split:
            spreadsheet = client.open_by_url(USERS.get_split_url(username))
        else:
            spreadsheet = client.open_by_url(USERS.get_url(username))
        logger.debug("Sheet for user %s has been retrieved, time: [%.2fs]", username, time.time() - start)

        logger.debug("Getting worksheet for user %s...", username)
        sheet = spreadsheet.worksheet(month)
        logger.debug("Worksheet for user %s has been retrieved, time: [%.2fs]", username, time.time() - start)

        logger.debug("Getting col_values for user %s...", username)
        # ③ API call: trova la prima riga vuota (col_values è più leggero di range)
        col_values = sheet.col_values(1)
        logger.debug("Col_values for user %s has been retrieved, time: [%.2fs]", username, time.time() - start)
        try:
            logger.debug("Getting index for user %s...", username)
            index = col_values.index('') + 1
            logger.debug("Index for user %s has been retrieved, time: [%.2fs]", username, time.time() - start)
        except ValueError:
            # Nessuna cella vuota trovata → aggiungi dopo l'ultima riga
            logger.debug("No empty cell found for user %s...", username)
            index = len(col_values) + 1
            logger.debug("Index for user %s has been set to %d, time: [%.2fs]", username, index, time.time() - start)

        logger.debug("Updating sheet for user %s...", username)
        if row.split:
            logger.debug("Split case for user %s...", username)
            sheet.batch_update([
                {'range': f'A{index}', 'values': [[row.description]]},
                {'range': f'B{index}', 'values': [[now.day]]},
                {'range': f'E{index}', 'values': [[row.price]]},
            ])
            logger.debug("Sheet for user %s has been updated, time: [%.2fs]", username, time.time() - start)
        else:
            # ④ API call UNICA: aggiorna tutte e 3 le celle in un solo batch
            logger.debug("Normal case for user %s...", username)
            sheet.batch_update([
                {'range': f'A{index}', 'values': [[row.description]]},
                {'range': f'B{index}', 'values': [[now.day]]},
                {'range': f'C{index}', 'values': [[row.price]]},
            ])
            logger.debug("Sheet for user %s has been updated, time: [%.2fs]", username, time.time() - start)

    except PermissionError as e:
        logger.error("Errore di permessi")
        raise PermissionError(
            "Accesso negato allo Sheet. Per ottenerlo, accedere allo "
            "sheet e condividerlo con l'user del bot <code>sa-cisot-bot@eighth-brace-469407-e3.iam.gserviceaccount.com</code>."
        ) from e
    finally:
        if client is not None:
            client.http_client.session.close()
        elapsed = time.time() - start
        logger.info("add_row terminata in %.2fs (riga %d)", elapsed)
