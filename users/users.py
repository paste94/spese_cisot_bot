import json
import os

class Users:
    def __init__(self) -> None:
        self.filename = 'users/users.json'
        self._last_mtime: float = 0.0
        self._load()

    def _load(self):
        """Carica il file di configurazione"""
        with open(self.filename, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._last_mtime = os.path.getmtime(self.filename)

    def _reload_if_changed(self) -> None:
        """Ricarica il file se è stato modificato."""
        try:
            mtime = os.path.getmtime(self.filename)
        except FileNotFoundError:
            return
        if mtime != self._last_mtime:
            self._load()

    def get_url(self, username: str) -> str:
        """
        Recupera un utente
        """
        self._reload_if_changed()
        
        for user in self._data['USER_LIST']:
            if user['USERNAME'] == username:
                return user['GSHEET_URL']
        
        raise ValueError(f'User {username} not found')

    def is_authorized(self, username) -> bool: 
        self._reload_if_changed()
        
        for user in self._data['USER_LIST']:
            if user['USERNAME'] == username:
                return True
        
        return False

    def update_url(self, username: str, new_url: str) -> str:
        self._reload_if_changed()

        for user in self._data['USER_LIST']:
            if user['USERNAME'] == username:
                user['GSHEET_URL'] = new_url
                with open(self.filename, "w") as f:
                    json.dump(self._data, f, indent=4)
                return f'{username} url updated correctly'
        
        raise ValueError(f'User {username} not found')

        

