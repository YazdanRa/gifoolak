from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler


def start(update: Update, context):
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Hi')
    return ConversationHandler.END


HANDLER = CommandHandler('start', start)
