import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVER_PATH = os.path.join(BASE_DIR, "TidetronCatalogCover.jpg")
CATALOG_PATH = os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf")

def vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tidetron Peptides", callback_data="vendor_tidetron")]
    ])

async def send_tidetron(message: types.Message):
    await message.answer(
        "✅ <b>VERIFIED VENDOR</b>\n\n"
        "<b>Tidetron Peptides</b>\n"
        "Sales contact: <b>Liao</b>\n\n"
        "📍 <b>Warehouse:</b> China &amp; USA\n"
        "🚚 <b>Shipping:</b> 10–15 days (China) · 3–5 days (USA)\n"
        "💳 <b>Payment:</b> Alibaba, PayPal, Apple Pay, Crypto &amp; more",
        parse_mode="HTML",
    )

    await message.answer_photo(FSInputFile(COVER_PATH))

    await message.answer_document(
        FSInputFile(CATALOG_PATH),
        caption="📄 <b>Full price list</b>",
        parse_mode="HTML",
    )

    await message.answer(
        "💬 You can now continue chatting directly with the vendor representative."
    )

@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject):
    if command.args == "tidetron":
        await send_tidetron(message)
        return

    await message.answer(
        "🛡️ <b>Verified Vendors</b>\n\nChoose a vendor:",
        reply_markup=vendor_keyboard(),
        parse_mode="HTML",
    )

@dp.callback_query(F.data == "vendor_tidetron")
async def vendor_tidetron(callback: types.CallbackQuery):
    await callback.answer()
    await send_tidetron(callback.message)

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
