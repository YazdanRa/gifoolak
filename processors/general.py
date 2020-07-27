import logging

from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler


def _error(update, context):
    """Log Errors caused by Updates."""
    logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, context.error)
    chat_id = update.message.chat.id
    context.bot.delete_message(chat_id, update.message.message_id)
    context.bot.send_message(chat_id, ('Oops...\n' +
                                       'Something went wrong! Try again:'))
    return


def _cancel(update, context):
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Process was canceled!', reply_markup=ReplyKeyboardRemove())

    context.user_data.clear()
    return ConversationHandler.END
