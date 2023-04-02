from telegram.ext import Updater, CommandHandler
import utils
import logging
import telegram
import config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

token = config.telegram['token']
bot = telegram.Bot(token=token)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Hello , Thanks for choosing us!!")

    context.job_queue.run_repeating(callback_minute, interval=120, first=10,
                                    context=update.message.chat_id)


def tele_send_text(posts, context, chat_id):
    for post in posts:
        msg = f"""
            Subreddit : {post.get('subreddit','Null')} \n
            Title : {post.get('title','Null')} \n
            Posted Ago : {post.get('posted_ago','Null')} hours \n
            Url : {post.get('url','Null')} \n
            Text : {post.get('selftext','Null')}
            """
        context.bot.send_message(chat_id=chat_id, text=msg)



def callback_minute(context):
    chat_id = context.job.context
    filtered_sub_posts = utils.get_all_posts()
    for sub_post in filtered_sub_posts:
        tele_send_text(sub_post, context,chat_id)


def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, pass_job_queue=True))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
