#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"
import telebot
from modules.TgBotAdapter import TgBotAdapter
from modules.TgBotAdapter import BotCommands as Commands

# create bot
BOT_TOKEN = ""

bot = telebot.TeleBot(BOT_TOKEN)
app = TgBotAdapter(bot)


# get main message
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == Commands.start:
        app.start_handler(message.from_user.id)
    elif message.text == Commands.day_timetable:
        if app.tg_user(message.from_user.id):
            app.send_day_lessons(message.from_user.id)
    elif message.text == Commands.current_lesson:
        if app.tg_user(message.from_user.id):
            app.send_current_lesson(message.from_user.id)
    elif message.text == Commands.about:
        app.about(message.from_user.id)
    elif message.text == Commands.commands:
        app.help(message.from_user.id)
    else:
        app.parse_other_message(message.from_user.id,message.text)


bot.polling(none_stop=True, interval=0)

