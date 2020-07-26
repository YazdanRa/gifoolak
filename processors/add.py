from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

from models import User, Gif, Keyword
from processors.general import error, cancel

GIF, KEYWORD, PUBLIC = range(3)


def start_add_gif(update: Update, context: CallbackContext):
    context.user_data.clear()
    chat_id = update.message.from_user.id
    context.bot.send_message(chat_id, 'Send your Gif!', reply_markup=ReplyKeyboardRemove())
    return GIF


def get_gif(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id

    try:
        gif = context.bot.getFile(update.message.animation)
    except:
        context.bot.send_message(chat_id, 'Please send a Gif!')
        return

    gif = Gif.insert({
        Gif.user: User.get(User.chat_id == chat_id),
        Gif.file_id: gif.file_id,
        Gif.file_path: gif.file_path,
        Gif.file_size: gif.file_size,
    }).execute()
    context.user_data['gif'] = gif
    context.bot.send_message(chat_id,
                             'Now send your keywords as many as you want!\nsubsequently send *DONE* :)',
                             reply_markup=ReplyKeyboardMarkup([['DONE']]),
                             parse_mode='Markdown')
    return KEYWORD


def get_keyword(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    gif = Gif.get(Gif.id == context.user_data['gif'])
    text = update.message.text
    if text == 'DONE':
        context.bot.send_message(chat_id,
                                 'do you agree to show this gif to others?!',
                                 reply_markup=ReplyKeyboardMarkup([['YES'], ['NO']]))
        return PUBLIC

    try:
        keyword = Keyword.get(Keyword.text == text)
        if keyword in gif.keywords:
            context.bot.send_message(chat_id, 'You have already added this keyword!')
        else:
            gif.keywords.add(keyword)
            context.bot.send_message(chat_id, 'keyword successfully added!')
    except:
        keyword = Keyword.insert({
            Keyword.text: text
        }).execute()
        gif.keywords.add(keyword)
        context.bot.send_message(chat_id, 'keyword successfully added!')

    return


def is_public(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    gif = Gif.get(Gif.id == context.user_data['gif'])
    public = update.message.text
    if public == 'YES':
        gif.is_public = True
        gif.save()
    else:
        gif.is_public = False
        gif.save()
    context.bot.send_message(chat_id, 'Your gif successfully added :)', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('add', start_add_gif),
    ],

    states={

        GIF: [MessageHandler(Filters.animation, get_gif)],

        KEYWORD: [MessageHandler(Filters.text, get_keyword)],

        PUBLIC: [MessageHandler(Filters.regex(r'(YES|NO)'), is_public)]
    },

    fallbacks=[
        MessageHandler(Filters.command, cancel),
        MessageHandler(Filters.text('Cancel'), cancel),
        MessageHandler(Filters.all, error)
    ],

    allow_reentry=True,
)
