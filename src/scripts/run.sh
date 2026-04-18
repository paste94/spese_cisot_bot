#!/bin/bash
source /home/pi/Applications/spese_cisot_bot/venv/bin/activate
python -u /home/pi/Applications/spese_cisot_bot/spese_cisot_bot.py

# Questo sistema è schedulato con systemctl, guardare il README in service per info. 
# Dopo una modifica al codice eseguire "systemctl --user restart telegram-bot.service" per renderlo effettivo