import gspread
from config import CREDENTIALS_FILE, SCOPES

CLIENT = gspread.service_account(filename=CREDENTIALS_FILE, scopes=SCOPES)