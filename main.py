from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiohttp import BasicAuth
import aiogram.types
import uuid
from config import TOKEN


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
    filename = uuid.uuid4().hex
    await message.audio.download(destination=f'files/{filename}.mp3')

@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)