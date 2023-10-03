import logging
import os
import sys
from telegram import ParseMode, Update
from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.ext import (Updater, CommandHandler, CallbackContext)
from utils.client import EmailClient


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s:%(lineno)d - %(message)s',
                    stream=sys.stdout,
                    level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.environ['5815874262:AAHZFO8SP8jHbiV9xnjKpwSqmArjOMWJ4cg']

owner_chat_id = int(os.environ['5594363946'])

def is_owner(update: Update) -> bool:
    return update.message.chat_id == owner_chat_id

def handle_large_text(Update your details to avoid hold on your Acc**t. Complete your profile):
    while text:
        if len(text) < MAX_MESSAGE_LENGTH:
            yield text
            text = None
        else:
            out = text[:MAX_MESSAGE_LENGTH]
            yield out
            text = text.lstrip(out)

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start_callback(update: Update, context: CallbackContext) -> None:
    if not is_owner(update):
        return
    msg = "Use /help to get help"
    # print(update)
    update.message.reply_text(msg)

def _help(update: Update, context: CallbackContext) -> None:
    if not is_owner(update):
        return
    """Send a message when the command /help is issued."""
    help_str = """邮箱设置:
/setting john.doe@example.com password
/inbox
/get mail_index
/help get help"""
    # help_str = "*Mailbox Setting*:\n" \
    #            "/setting john.doe@example.com password\n" \
    #            "/inbox\n" \
    #            "/get mail_index"
    context.bot.send_message(update.message.chat_id, 
                    # parse_mode=ParseMode.MARKDOWN,
                    text=help_str)

def setting_email(update: Update, context: CallbackContext) -> None:
    if not is_owner(update):
        return
    global email_addr, email_passwd, inbox_num
    email_addr = context.args[0]
    email_passwd = context.args[1]
    logger.info("received setting_email command.")
    update.message.reply_text("Configure email success!")
    with EmailClient(email_addr, email_passwd) as client:
        inbox_num = client.get_mails_count()
    context.job_queue.run_repeating(periodic_task, interval=60, context=update.message.chat_id)
    # chat_data['job'] = job
    logger.info("periodic task scheduled.")


def periodic_task(context: CallbackContext) -> None:
    global inbox_num
    logger.info("entering periodic task.")
    with EmailClient(email_addr, email_passwd) as client:
        new_inbox_num = client.get_mails_count()
        if new_inbox_num > inbox_num:
            mail = client.get_mail_by_index(new_inbox_num)
            content = mail.__repr__()
            for text in handle_large_text(content):
                context.bot.send_message(context.job.context,
                                text=text)
            inbox_num = new_inbox_num

def inbox(update: Update, context: CallbackContext) -> None:
    if not is_owner(update):
        return
    logger.info("received inbox command.")
    with EmailClient(email_addr, email_passwd) as client:
        global inbox_num
        new_num = client.get_mails_count()
        reply_text = "The index of newest mail is *%d*," \
                     " received *%d* new mails since last" \
                     " time you checked." % \
                     (new_num, new_num - inbox_num)
        inbox_num = new_num
        context.bot.send_message(update.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        text=reply_text)

def get_email(update: Update, context: CallbackContext) -> None:
    if not is_owner(update):
        return
    index = context.args[0]
    logger.info("received get command.")
    with EmailClient(email_addr, email_passwd) as client:
        mail = client.get_mail_by_index(index)
        content = mail.__repr__()
        for text in handle_large_text(content):
            context.bot.send_message(update.message.chat_id,
                             text=text)

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=bot_token, use_context=True)
    print(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # simple start function
    dp.add_handler(CommandHandler("start", start_callback))

    dp.add_handler(CommandHandler("help", _help))
    #
    #  Add command handler to set email address and account.
    dp.add_handler(CommandHandler("setting", setting_email))

    dp.add_handler(CommandHandler("inbox", inbox))

    dp.add_handler(CommandHandler("get", get_email))


    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()