import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiohttp import BasicAuth
import aiogram.types
import uuid
from video_processing import YodaVideoProcessing
from config import TOKEN, DESTINATION_USER_AUDIO


PROXY_AUTH = BasicAuth(login='hrgsaMsTL4', password='w0ezUpFXuW')
bot = Bot(token=TOKEN, proxy='http://45.158.45.120:48608', proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler(content_types=types.ContentTypes.AUDIO)
async def process_audio(message: types.Message):
    filename = uuid.uuid4().hex + '.mp3'
    destination = DESTINATION_USER_AUDIO + filename
    await bot.send_message(message.from_user.id, 'Видео обрабатывается...')
    await message.audio.download(destination=destination)
    async with YodaVideoProcessing(destination) as yvp:
        output_path = await yvp.pipeline()
        with open(output_path, 'rb') as video:
            await bot.send_video(message.from_user.id, video)
    os.remove(destination)


if __name__ == '__main__':
    executor.start_polling(dp)