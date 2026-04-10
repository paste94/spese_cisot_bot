from gspread import authorize
from google.oauth2.service_account import Credentials
from config import CREDENTIALS_FILE, SCOPES

CLIENT = authorize(Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES))