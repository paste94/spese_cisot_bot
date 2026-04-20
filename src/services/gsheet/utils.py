from services.logger.logger import logger
import time

from gspread import NoValidUrlKeyFound
from config import MONTH_NAMES
from services.gsheet.client import CLIENT
from services.gsheet.exceptions import UnknownLinkError
from services.users.users import USERS
from datetime import datetime

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
        spreadsheet = CLIENT.open_by_url(url)
        name = spreadsheet.title
        _sheet_name_cache[url] = (name, now)
        return name
    except Exception as e:
        if isinstance(e, NoValidUrlKeyFound):
            raise UnknownLinkError("Link Google Sheet non valido")
        if isinstance(e, PermissionError):
            raise PermissionError(
                "Accesso negato allo Sheet. Per ottenerlo, accedere allo "
                "sheet e condividerlo con l'user del bot."
            )
        raise e

def add_row(row, username: str):
    """Aggiunge una riga allo sheet usando solo 3 chiamate API (prima erano 7)."""
    start = time.time()

    now = datetime.now()
    month = MONTH_NAMES[now.month]

    spreadsheet = CLIENT.open_by_url(USERS.get_url(username))
    sheet = spreadsheet.worksheet(month)

    col_values = sheet.col_values(1)
    try:
        index = col_values.index('') + 1
    except ValueError:
        index = len(col_values) + 1

    sheet.batch_update([
        {'range': f'A{index}', 'values': [[row['description']]]},
        {'range': f'B{index}', 'values': [[now.day]]},
        {'range': f'C{index}', 'values': [[row['price']]]},
        {'range': f'F{index}', 'values': [[row['split']]]},
    ])

    elapsed = time.time() - start
    logger.info("add_row completata in %.2fs (riga %d)", elapsed, index)