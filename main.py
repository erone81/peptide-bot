import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Test Vendor", callback_data="vendor_test")]
    ])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "🛡️ <b>Verified Vendors</b>\n\nChoose a vendor:",
        reply_markup=vendor_keyboard(),
        parse_mode="HTML",
    )

@dp.callback_query(F.data == "vendor_test")
async def vendor_test(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📋 <b>Price list</b>\n"
        "The price list image will appear here soon.\n\n"
        "📦 <b>Delivery and rules</b>\n"
        "• Orders are packed in standard factory kits of 10\n"
        "• After this message you continue chatting directly with the vendor\n"
        "• Agree the final offer with the vendor before payment",
        parse_mode="HTML",
    )

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
