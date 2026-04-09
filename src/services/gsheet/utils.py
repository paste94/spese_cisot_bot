from gspread import NoValidUrlKeyFound
from config import MONTH_NAMES
from services.gsheet.exceptions import UnknownLinkError
from services.users.users import USERS
from spese_cisot_bot import CLIENT
from datetime import datetime

def get_sheet_name(url: str) -> str:
    try:
        spreadsheet = CLIENT.open_by_url(url)
        return spreadsheet.title
    except Exception as e:
        if isinstance(e, NoValidUrlKeyFound):
            raise UnknownLinkError("Link Google Sheet non valido")
        if isinstance(e, PermissionError):
            raise PermissionError("Accesso negato allo Sheet. Per ottenerlo, accedere allo sheet e condividerlo con l'user del bot.")
        raise e
    
def add_row(row, username: str):
    now = datetime.now()
    month = MONTH_NAMES[now.month]
    # Gets right worksheet

    spreadsheet = CLIENT.open_by_url(USERS.get_url(username))
    sheet = spreadsheet.worksheet(month)

    # Finds the first empty row
    cols = sheet.range(1, 1, sheet.row_count, 1)
    index  = [cell.value for cell in cols].index('')+1

    sheet.update_cell(index, 1, row['description'])
    sheet.update_cell(index, 2, now.day)
    sheet.update_cell(index, 3, row['price'])
    sheet.update_cell(index, 6, row['split'])