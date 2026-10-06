import asyncio
import json
import os
import re
import secrets
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Фиксирано ID на групата Tidetron Sales TPVH
GROUP_ID = -1004387055068
VENDOR_USERNAME = "g3orgel"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/app/data" if os.path.exists("/app/data") else BASE_DIR

COVER_PATH = os.path.join(BASE_DIR, "TidetronCatalogCover.jpg")
HORIZONTAL_BANNER_PATH = os.path.join(BASE_DIR, "TidetronCatalogCoverHorizontal.jpg")
CATALOG_PATH = os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf")
DATA_PATH = os.path.join(DATA_DIR, "routes.json")

group_id = GROUP_ID
buyer_topics = {}
topic_buyers = {}
buyer_names = {}
pending = {}
locked_offers = []
next_offer_number = 1001
proof_topic_id = None
lock_button_ids = {}
waiting_offer_text = {}
waiting_total = {}
pending_connect_thread = None

PRICE_REGEX = (
    r"(?i)(?:total|amount|price|final|sum|cost|pay|合计|总计|总价|金额|最终价)\s*[:：]?\s*\$?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)"
)

def vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tidetron Peptides", callback_data="vendor_tidetron")]
    ])

def confirm_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data=f"yes:{key}")],
        [InlineKeyboardButton(text="✏️ Change something", callback_data=f"no:{key}")],
    ])

def make_offer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Make offer", callback_data="start_make_offer")]
    ])

# Бутон за публичната визитка в раздела Verified Vendors
def public_vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Chat with Tidetron",
            url="https://t.me/TrustedPeptideVendorsBot?start=tidetron"
        )]
    ])

def topic_name(user: types.User) -> str:
    who = user.username or user.full_name or "Buyer"
    return f"Buyer · {who}"[:120]

def money(value):
    return f"{value:.2f} USD"

def commission_of(total):
    return round(float(total) * 0.10, 2)

def clean_number(raw):
    text = (raw or "").strip().replace(" ", "")
    if re.fullmatch(r"[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?", text):
        text = text.replace(",", "")
    elif re.fullmatch(r"[0-9]+,[0-9]{1,2}", text):
        text = text.replace(",", ".")
    elif not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", text):
        return None
    try:
        value = float(text)
        return round(value, 2) if value > 0 else None
    except ValueError:
        return None

def parse_only_number(text):
    if not text:
        return None
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[\$€£]|usd|eur|дол.*|bucks", "", cleaned).strip()
    return clean_number(cleaned)

def detect_total(text):
    text = text or ""
    found = re.findall(PRICE_REGEX, text)
    if found:
        return clean_number(found[-1])
    standalone = re.findall(r"(?i)(?:^\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:\$|usd)?\s*$)", text, re.MULTILINE)
    if standalone:
        return clean_number(standalone[-1])
    return None

def leaks_commission(text):
    low = (text or "").lower()
    return "commission" in low or "комисион" in low

def buyer_label(user: types.User) -> str:
    username = f"@{user.username}" if user.username else "no username"
    return f"{user.full_name} ({username})"

def buyer_offer_text(offer):
    text = (offer.get("text") or "").strip()
    detected = detect_total(text)
    if detected is not None and abs(detected - float(offer["total"])) < 0.001:
        return text
    return f"{text}\n\nTotal: {money(offer['total'])}"

def save_data():
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "group_id": group_id,
                    "buyer_topics": buyer_topics,
                    "topic_buyers": topic_buyers,
                    "buyer_names": buyer_names,
                    "pending": pending,
                    "locked_offers": locked_offers,
                    "next_offer_number": next_offer_number,
                    "proof_topic_id": proof_topic_id,
                },
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global group_id, buyer_topics, topic_buyers, buyer_names
    global pending, locked_offers, next_offer_number, proof_topic_id
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        group_id = data.get("group_id") or GROUP_ID
        buyer_topics = {int(k): v for k, v in data.get("buyer_topics", {}).items()}
        topic_buyers = {int(k): v for k, v in data.get("topic_buyers", {}).items()}
        buyer_names = {int(k): v for k, v in data.get("buyer_names", {}).items()}
        pending = data.get("pending", {})
        locked_offers = data.get("locked_offers", [])
        next_offer_number = int(data.get("next_offer_number", 1001))
        proof_topic_id = data.get("proof_topic_id")
    except Exception as e:
        print(f"Error loading routes.json: {e}")

def replace_open_offers(buyer_id):
    for offer in pending.values():
        if offer.get("buyer_id") == buyer_id and offer.get("status") in ("draft", "need_total", "waiting"):
            offer["status"] = "replaced"

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
    if os.path.exists(COVER_PATH):
        await message.answer_photo(FSInputFile(COVER_PATH))
    if os.path.exists(CATALOG_PATH):
        await message.answer_document(
            FSInputFile(CATALOG_PATH),
            caption="📄 <b>Full price list</b>",
            parse_mode="HTML",
        )
    await message.answer(
        "💬 <b>Continue with the vendor.</b>\n\n"
        "Just write your message here.",
        parse_mode="HTML"
    )

async def proof_thread():
    global proof_topic_id
    if proof_topic_id:
        return proof_topic_id
    topic = await bot.create_forum_topic(group_id, "Locked offers")
    proof_topic_id = topic.message_thread_id
    save_data()
    return proof_topic_id

async def clear_lock_button(thread_id):
    message_id = lock_button_ids.pop(thread_id, None)
    if message_id and group_id:
        try:
            await bot.delete_message(group_id, message_id)
        except Exception:
            pass

async def send_confirm_card(key, offer):
    offer["status"] = "waiting"
    save_data()
    await bot.send_message(
        offer["buyer_id"],
        "Please confirm this offer:\n\n"
        f"{buyer_offer_text(offer)}\n\n"
        "Press Confirm only if everything is correct.",
        reply_markup=confirm_keyboard(key),
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

# Команда за публикуване на изчистената визитка в раздела Verified Vendors
@dp.message(Command("post_vendor"))
async def post_vendor_card(message: types.Message):
    username = (message.from_user.username or "").lower()
    if username != VENDOR_USERNAME.lower():
        return
    
    caption_text = (
        "<b>1. Tidetron Peptides</b>\n"
        "🛡️ Verified Vendor"
    )
    
    thread_id = message.message_thread_id
    banner_file = HORIZONTAL_BANNER_PATH if os.path.exists(HORIZONTAL_BANNER_PATH) else COVER_PATH
    
    if os.path.exists(banner_file):
        await bot.send_photo(
            message.chat.id,
            FSInputFile(banner_file),
            caption=caption_text,
            reply_markup=public_vendor_keyboard(),
            parse_mode="HTML",
            message_thread_id=thread_id
        )
    else:
        await bot.send_message(
            message.chat.id,
            caption_text,
            reply_markup=public_vendor_keyboard(),
            parse_mode="HTML",
            message_thread_id=thread_id
        )
    try:
        await message.delete()
    except Exception:
        pass

@dp.message(Command("vendor"))
async def register_vendor(message: types.Message):
    global group_id
    if message.chat.type == "private":
        await message.answer("Write /vendor inside the group.")
        return
    username = (message.from_user.username or "").lower()
    if username != VENDOR_USERNAME.lower():
        await message.answer("Only GeorgeL can configure this group.")
        return
    group_id = message.chat.id
    save_data()
    await message.answer("Connected.\n\nGroup ID is permanently registered.")

@dp.message(Command("connect"))
async def connect_topic(message: types.Message):
    global pending_connect_thread
    if message.chat.type == "private":
        await message.answer("Write /connect inside a buyer topic.")
        return
    if (message.from_user.username or "").lower() != VENDOR_USERNAME.lower():
        return
    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        await message.answer("Open the buyer topic and write /connect there.")
        return
    pending_connect_thread = thread_id
    await message.answer("Waiting for
