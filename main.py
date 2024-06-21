from bot import bot
from dotenv import load_dotenv
from os.path import join, dirname
import locale

if __name__ == '__main__':
    locale.setlocale(locale.LC_TIME, 'rus')
    load_dotenv(join(dirname(__file__), '.env'))
    print("Starting polling.")
    bot.infinity_polling()
