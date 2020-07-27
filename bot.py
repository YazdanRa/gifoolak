import logging
import os
from uuid import uuid4

from telegram import InlineQueryResultCachedGif, Update
from telegram.ext import Updater, InlineQueryHandler, MessageHandler, Filters, CallbackContext

from models import *
# Enable logging
from processors import add, greetings
from processors.general import _error
from processors.save_data import save_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment():
    from dotenv import load_dotenv
    load_dotenv()

    # OR, the same with increased verbosity:
    load_dotenv(verbose=True)

    # OR, explicitly providing path to '.env'
    from pathlib import Path  # python3 only
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)


load_environment()

database.init(os.getenv("DATABASE"))
database.connect()
database.create_tables([
    User,
    Message,
    Gif,
    Keyword,
    KeywordGif,
])


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def inlinequery(update: Update, context: CallbackContext):
    """Handle the inline query."""
    query = update.inline_query.query.lower()

    results = []
    for keyword in Keyword.select().where(Keyword.text == query):
        for gif in keyword.gif:
            result = InlineQueryResultCachedGif(
                id=uuid4(),
                gif_file_id=gif.file_id,
            )
            if not result in results:
                results.append(result)

    update.inline_query.answer(results)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("TOKEN"), use_context=True)

    # Get the dispatcher to register handlers
    bot = updater.dispatcher

    # on different commands - answer in Telegram
    bot.add_handler(MessageHandler(Filters.all, save_data), group=0)
    bot.add_handler(greetings.HANDLER, group=1)
    bot.add_handler(add.HANDLER, group=2)

    # on noncommand i.e message - echo the message on Telegram
    bot.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    bot.add_error_handler(_error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
