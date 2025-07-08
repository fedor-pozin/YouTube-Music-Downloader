import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp
from config import TG_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = TG_TOKEN  # Замените на реальный токен

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Конфигурация yt-dlp БЕЗ FFmpeg
ydl_opts = {
    'format': 'bestaudio/best',  # Лучший аудиопоток
    'outtmpl': '%(title)s.%(ext)s',
    'retries': 3,
    'socket_timeout': 30,
    'quiet': True,
    'no_warnings': True,
    'extract_audio': True,  # Извлекаем только аудио
    'keepvideo': False,  # Не сохраняем видео
    'noplaylist': True,  # Только одиночные видео
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎵 <b>YouTube Audio Downloader</b>\n\n"
        "Пришли мне ссылку на YouTube видео, и я скачаю аудио (без конвертации).",
        parse_mode="HTML"
    )


@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if not ('youtube.com' in text or 'youtu.be' in text):
        await message.reply("Пожалуйста, пришлите корректную ссылку на YouTube видео")
        return

    try:
        msg = await message.reply("⏳ <b>Начинаю загрузку...</b>", parse_mode="HTML")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, text, download=True)
            filename = ydl.prepare_filename(info)

            # Отправляем оригинальный аудиофайл (без конвертации)
            with open(filename, 'rb') as audio:
                await message.reply_audio(
                    audio=types.BufferedInputFile(audio.read(), filename=os.path.basename(filename)),
                    caption=f"🎧 <b>{info.get('title', 'Аудио')}</b>",
                    parse_mode="HTML"
                )

            # Удаляем временный файл
            os.remove(filename)

        await msg.edit_text("✅ <b>Загрузка завершена!</b>", parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await message.reply(f"❌ <b>Ошибка:</b> {str(e)}", parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Запуск бота...")
    asyncio.run(main())