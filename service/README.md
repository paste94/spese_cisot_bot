Copy .service file under .config/systemd/user folder, then run 

# Ricarica configurazione user
systemctl --user daemon-reload

# Abilita all'avvio (per l'utente corrente)
systemctl --user enable telegram-bot.service

# Avvia subito
systemctl --user start telegram-bot.service

| Comando                                    | Descrizione               |
| ------------------------------------------ | ------------------------- |
| systemctl --user status telegram-bot       | Stato del servizio dev​   |
| systemctl --user start telegram-bot        | Avvia                     |
| systemctl --user stop telegram-bot         | Ferma                     |
| systemctl --user list-units --type=service | Tutti i tuoi servizi user |
| journalctl --user -u telegram-bot -f       | Log in tempo reale        |

# Lista servizi user attivi
systemctl --user --type=service --state=running

# Posizione del file
systemctl --user status telegram-bot | head -5


# Dopo una modifica al codice eseguire 
systemctl --user restart telegram-bot.service
