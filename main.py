import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVER_PATH = os.path.join(BASE_DIR, "TidetronCatalogCover.jpg")
CATALOG_PATH = os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf")

VENDOR_USERNAME = "g3orgel"
vendor_id = None
routes = {}

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
        "💬 Continue with the vendor.\n\nJust write your message here."
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

@dp.message(Command("vendor"))
async def register_vendor(message: types.Message):
    global vendor_id
    username = (message.from_user.username or "").lower()
    if username != VENDOR_USERNAME:
        await message.answer("This account is not the vendor.")
        return
    vendor_id = message.from_user.id
    await message.answer(
        "Vendor mode is on.\n\nBuyer messages will arrive here. Reply to a message to answer."
    )

@dp.message(F.chat.type == "private", F.text)
async def relay(message: types.Message):
    global vendor_id
    if message.text.startswith("/"):
        return

    if message.from_user.id == vendor_id:
        replied = message.reply_to_message
        if replied and replied.message_id in routes:
            buyer_id = routes[replied.message_id]
            await bot.send_message(
                buyer_id,
                f"Liao · Tidetron Peptides\n\n{message.text}",
            )
        else:
            await message.answer("Reply to the buyer’s message to send your answer.")
        return

    if not vendor_id:
        await message.answer("The vendor is not connected yet. Please try again in a minute.")
        return

    sent = await bot.send_message(
        vendor_id,
        f"Buyer message:\n\n{message.text}\n\n↩️ Reply to this message.",
    )
    routes[sent.message_id] = message.chat.id

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
