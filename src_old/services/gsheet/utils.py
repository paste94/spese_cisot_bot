import gspread
from config import SCOPES
from config import CREDENTIALS_FILE
from model.row import Row
import time
import logging

from gspread import NoValidUrlKeyFound
from config import MONTH_NAMES
# from services.gsheet.client import CLIENT
from services.gsheet.exceptions import UnknownLinkError
from services.users.users import USERS
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Cache nomi sheet (TTL 5 minuti) ──────────────────────────
_sheet_name_cache: dict = {}   # url -> (name, timestamp)
_CACHE_TTL = 300               # secondi

def get_sheet_name(url: str) -> str:
    """Restituisce il titolo dello spreadsheet, con cache di 5 minuti."""
    now = time.time()

    # Controlla la cache
    if url in _sheet_name_cache:
        name, cached_at = _sheet_name_cache[url]
        if now - cached_at < _CACHE_TTL:
            return name

    try:
        client = gspread.service_account(filename=CREDENTIALS_FILE, scopes=SCOPES)
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
        client.http_client.session.close()

def add_row(row: Row, username: str):
    """Aggiunge una riga allo sheet usando solo 3 chiamate API (prima erano 7)."""
    try : 
        start = time.time()

        now = datetime.now()
        month = MONTH_NAMES[now.month]

        client = gspread.service_account(filename=CREDENTIALS_FILE, scopes=SCOPES)

        if row.split:
            # ① + ② API calls: apre spreadsheet e worksheet
            spreadsheet = client.open_by_url(USERS.get_split_url(username))
        else:
        # ① + ② API calls: apre spreadsheet e worksheet
            spreadsheet = client.open_by_url(USERS.get_url(username))
        sheet = spreadsheet.worksheet(month)

        # ③ API call: trova la prima riga vuota (col_values è più leggero di range)
        col_values = sheet.col_values(1)
        try:
            index = col_values.index('') + 1
        except ValueError:
            # Nessuna cella vuota trovata → aggiungi dopo l'ultima riga
            index = len(col_values) + 1

        if row.split:
            sheet.batch_update([
                {'range': f'A{index}', 'values': [[row.description]]},
                {'range': f'B{index}', 'values': [[now.day]]},
                {'range': f'E{index}', 'values': [[row.price]]},
            ])
        else:
            # ④ API call UNICA: aggiorna tutte e 4 le celle in un solo batch
            sheet.batch_update([
                {'range': f'A{index}', 'values': [[row.description]]},
                {'range': f'B{index}', 'values': [[now.day]]},
                {'range': f'C{index}', 'values': [[row.price]]},
            ])

    except PermissionError as e:
        logger.error("Errore di permessi")
        raise PermissionError(
            "Accesso negato allo Sheet. Per ottenerlo, accedere allo "
            "sheet e condividerlo con l'user del bot <code>sa-cisot-bot@eighth-brace-469407-e3.iam.gserviceaccount.com</code>."
        ) from e
    finally:
        client.http_client.session.close() 
        elapsed = time.time() - start
        logger.info("add_row completata in %.2fs (riga %d)", elapsed)
