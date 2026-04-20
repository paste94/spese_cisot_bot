""" Configuration settings and constants for the bot. """

from pathlib import Path

CREDENTIALS_FILE = "g-sheet-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DIV_STRINGS = ['diviso', 'divisa', 'div', 'splittata', 'splittato', 'split']
TIMEOUT_SECONDS = 30
MONTH_NAMES = {
    1: "Gen",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "Mag",
    6: "Giu",
    7: "Lug",
    8: "Ago",
    9: "Set",
    10: "Ott",
    11: "Nov",
    12: "Dic"
}
# ── Logging con rotazione giornaliera (max 7 giorni) ─────────
LOG_PATH=Path.cwd() / "log"
LOG_FILENAME="bot.log"
LOG_ERROR_FILENAME="error.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"