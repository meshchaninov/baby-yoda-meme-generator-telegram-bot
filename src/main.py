import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiohttp import BasicAuth
import aiogram.types
from aiogram.dispatcher.webhook import get_new_configured_app
from video_processing import YodaVideoProcessing

PROXY_LOGIN=os.getenv('PROXY_LOGIN')
PROXY_PASS=os.getenv('PROXY_PASS')
PROXY_URL=os.getenv('PROXY_URL')
TOKEN=os.environ['TOKEN']
BASE_DIR = os.getcwd()
DESTINATION_USER_AUDIO = BASE_DIR + '/files/audio/user/'

if PROXY_LOGIN and PROXY_PASS:
    PROXY_AUTH = BasicAuth(login=PROXY_LOGIN, password=PROXY_PASS)
else:
    PROXY_AUTH = None

if PROXY_URL:
    bot = Bot(token=TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
else:
    bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

GREETINGS = "Привет! Отправь мне музыкальный файл в формате mp3, и я из него сделаю видео-мем с маленьким йодой из сериала Мандалорец (P.S. находится пока в стадии бета!)"

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(GREETINGS)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(GREETINGS)

@dp.message_handler(content_types=types.ContentTypes.AUDIO)
async def process_audio(message: types.Message):
    try:
        filename = uuid.uuid4().hex + '.mp3'
        destination = DESTINATION_USER_AUDIO + filename
        await bot.send_message(message.from_user.id, 'Видео обрабатывается...')
        await message.audio.download(destination=destination)
        async with YodaVideoProcessing(destination) as yvp:
            output_path = await yvp.pipeline()
            with open(output_path, 'rb') as video:
                await bot.send_video(message.from_user.id, video)
        os.remove(destination)
    except Exception as e:
        await bot.send_message(message.from_user.id, f'🤒 соррии что-то пошло не так, вышлите это админу: {e}')

async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)