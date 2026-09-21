import asyncio
import logging
import urllib.parse
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile

# Токен Render серверинин жөндөөлөрүнөн алынат
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Салам! Мен сүрөт жараткан акысыз ботмун.\n\n"
        "Мага англисче текст жөнөтүңүз.\n"
        "Мисалы: *A cat in space*",
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def generate_image_handler(message: types.Message):
    prompt_text = message.text
    status_msg = await message.answer("⏳ Сүрөт даярдалууда (5-10 секунда)...")

    encoded_prompt = urllib.parse.quote(prompt_text)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={asyncio.get_event_loop().time()}"

    timeout = aiohttp.ClientTimeout(total=30)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    img_data = await resp.read()
                    photo_file = BufferedInputFile(img_data, filename="image.jpg")
                    await message.answer_photo(
                        photo=photo_file,
                        caption=f"✨ **Промпт:** {prompt_text}",
                        parse_mode="Markdown"
                    )
                    await status_msg.delete()
                else:
                    await status_msg.edit_text("❌ Сервер ашыкча жүктөлдү. Бир аздан кийин кайра аракет кылыңыз.")

    except Exception as e:
        logging.exception("Error during generation:")
        await status_msg.edit_text(f"❌ Ката кетти:\n`{str(e)}`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
