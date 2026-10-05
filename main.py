import asyncio
import json
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
DATA_PATH = os.path.join(BASE_DIR, "routes.json")

VENDOR_USERNAME = "g3orgel"
group_id = None
buyer_topics = {}
topic_buyers = {}

def vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tidetron Peptides", callback_data="vendor_tidetron")]
    ])

def topic_name(user: types.User) -> str:
    who = user.username or user.full_name or "Buyer"
    return f"Buyer · {who}"[:120]

def save_data():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "group_id": group_id,
                "buyer_topics": buyer_topics,
                "topic_buyers": topic_buyers,
            },
            f,
        )

def load_data():
    global group_id, buyer_topics, topic_buyers
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        group_id = data.get("group_id")
        buyer_topics = {int(k): v for k, v in data.get("buyer_topics", {}).items()}
        topic_buyers = {int(k): v for k, v in data.get("topic_buyers", {}).items()}
    except Exception:
        pass

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
    global group_id
    if message.chat.type == "private":
        await message.answer("Open the Tidetron Sales TPVH group and write /vendor there.")
        return
    username = (message.from_user.username or "").lower()
    if username != VENDOR_USERNAME:
        await message.answer("Only GeorgeL can connect this group.")
        return
    if not message.chat.is_forum:
        await message.answer("Topics are not enabled. Turn on Topics first.")
        return
    group_id = message.chat.id
    save_data()
    await message.answer(
        "Connected.\n\nEach buyer will appear as a separate topic. Open the topic and just write."
    )

@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def from_group(message: types.Message):
    if message.from_user and message.from_user.is_bot:
        return
    if message.text.startswith("/"):
        return
    if group_id is None or message.chat.id != group_id:
        return

    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        await message.reply("Open the buyer’s topic and write there.")
        return
    if thread_id not in topic_buyers:
        await message.reply("This topic is not linked to a buyer.")
        return

    buyer_id = topic_buyers[thread_id]
    try:
        await bot.send_message(buyer_id, f"Tidetron Peptides\n\n{message.text}")
    except Exception:
        await message.reply("The message was not delivered.")

@dp.message(F.chat.type == "private", F.text)
async def from_buyer(message: types.Message):
    if message.text.startswith("/"):
        return
    if (message.from_user.username or "").lower() == VENDOR_USERNAME:
        await message.answer("Open the Tidetron Sales TPVH group and write in the buyer’s topic.")
        return
    if not group_id:
        await message.answer("The vendor is not connected yet. Please try again in a minute.")
        return

    thread_id = buyer_topics.get(message.from_user.id)
    if not thread_id:
        try:
            topic = await bot.create_forum_topic(group_id, topic_name(message.from_user))
        except Exception as e:
            print("create topic failed:", e)
            await message.answer("The vendor chat is not ready yet. Please try again in a minute.")
            return
        thread_id = topic.message_thread_id
        buyer_topics[message.from_user.id] = thread_id
        topic_buyers[thread_id] = message.from_user.id
        save_data()
        username = f"@{message.from_user.username}" if message.from_user.username else "no username"
        await bot.send_message(
            group_id,
            f"New buyer\n{message.from_user.full_name}\n{username}\n\nWrite in this topic. The buyer stays in the same chat.",
            message_thread_id=thread_id,
        )

    await bot.send_message(group_id, message.text, message_thread_id=thread_id)

async def main():
    load_data()
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
