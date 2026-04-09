from bot_instance import bot
from services.settings.settings_state import SettingsState
from services.users.users import USERS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.utilities import handle_errors
from spese_cisot_bot import get_sheet_name

# /settings
@bot.message_handler(commands=['settings'])
def about_cmd(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

    current_url = USERS.get_url(message.from_user.username)
    old_urls = USERS.get_old(message.from_user.username)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"📊 {get_sheet_name(current_url)} (CURRENT)", callback_data='current'),
    )
    for index, url in enumerate(old_urls):
        markup.add(
            InlineKeyboardButton(f"📊 {get_sheet_name(url)}", callback_data=str(index)),
        )
    markup.add(
        InlineKeyboardButton(f"➕ Aggiungi nuovo sheet", callback_data='new'),
    )
    bot.set_state(message.from_user.id , SettingsState.waiting_sheet, message.chat.id)
    bot.send_message(message.chat.id, "Seleziona uno sheet", reply_markup=markup)

# BUTTONS HANDLER
@bot.callback_query_handler(func=lambda call: True)
@handle_errors(bot)
def handle_button_click(call):
    if not USERS.is_authorized(call.from_user.username):
        bot.reply_to(call.message, "❌ Non sei autorizzato a inviare messaggi.")
        return
    
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user_id = call.message.from_user.id
    if call.data == 'new': 
        bot.send_message(chat_id, '🔗 Inserisci il link del nuovo Google Sheet da usare:')
        bot.set_state(user_id , SettingsState.waiting_link, chat_id)
    if call.data == 'si':
        set_new_link_button(chat_id, call.from_user.username, call.from_user.id, True)
        bot.delete_state(user_id, chat_id)
    if call.data == 'no':
        set_new_link_button(chat_id, call.from_user.username, call.from_user.id, False)
        bot.delete_state(user_id, chat_id)
    if call.data == 'current':
        bot.send_message(chat_id, f"📊 Sheet corrente: {get_sheet_name(USERS.get_url(call.from_user.username))}")
        bot.delete_state(user_id, chat_id)
    if call.data.isdigit():
        switch_index_button(chat_id, call.from_user.username, int(call.data))
        bot.delete_state(user_id, chat_id)

# MESSAGE HANDLER (USED FOR LINK)
@bot.message_handler(state=SettingsState.waiting_link)
@handle_errors(bot)
def get_message(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

    link = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Sì (Default)", callback_data="si"),
        InlineKeyboardButton("❌ No", callback_data="no")
    )

    sheet_name = get_sheet_name(link)  # Verifica che il link sia valido
    bot.set_state(user_id , SettingsState.waiting_default, chat_id)
    with bot.retrieve_data(user_id, chat_id) as data:
        data["link"] = link

    bot.send_message(
        chat_id,
        f"📊 Sheet {sheet_name} trovato: Vuoi che questo sheet diventi il default?",
        reply_markup=markup
    )


### BUTTONS ###
def set_new_link_button(chat_id: str, username: str, user_id: str, update_current: bool):
    with bot.retrieve_data(user_id, chat_id) as data:
        link = data["link"]
    USERS.add_url_to_list(username, link, update_current=update_current)
    bot.send_message(chat_id, f'✅ Impostato nuovo sheet{" come default "if update_current else " "}correttamente.')

def switch_index_button(chat_id: str, username: str, index: int):
    USERS.switch_url_by_index(username, index)
    bot.send_message(chat_id, f'✅ Sheet cambiato correttamente.')
