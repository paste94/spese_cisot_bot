class UnauthorizedMessageError(Exception):
    """Eccezione sollevata quando un utente non autorizzato tenta di inviare un messaggio."""

    def __init__(self, user_name: str, telegram_id: int, message: str = None):
        self.user_name = user_name
        self.telegram_id = telegram_id
        self.message = message or f"Utente non autorizzato: {user_name} (ID: {telegram_id})"
        super().__init__(self.message)

    def __str__(self):
        return f"[UnauthorizedMessageError] user='{self.user_name}' telegram_id={self.telegram_id}"