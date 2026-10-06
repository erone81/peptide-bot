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

ADMIN_IDS = [8912162282]
ADMIN_USERNAMES = ["g3orgel", "georgel"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/app/data" if os.path.exists("/app/data") else BASE_DIR
DATA_PATH = os.path.join(DATA_DIR, "routes.json")

GROUP_ID = -1004387055068
group_id = GROUP_ID

# ==========================================
# КОНФИГУРАЦИЯ НА ВЕНДОРИТЕ
# ==========================================
VENDORS = {
    "tidetron": {
        "name": "1. TIDETRON PEPTIDES",
        "chat_name": "TIDETRON PEPTIDES",
        "sales_group_id": -1004387055068,
        "banner_path": os.path.join(BASE_DIR, "TidetronCatalogCoverHorizontal.jpg"),
        "catalog_path": os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf"),
        "button_text": "💬 Chat with Tidetron 🟢",
        "image_caption": (
            "<b>1. TIDETRON PEPTIDES</b>\n"
            "✅ <b>Verified Vendor</b>"
        ),
        "post_details": (
            "📍 <b>Warehouses:</b> China &amp; USA\n"
            "🚚 <b>Shipping:</b> 10–15 business days (Global) · 3–5 days (USA Domestic)\n"
            "💳 <b>Payment:</b> Alibaba Trade Assurance, PayPal, Apple Pay, Crypto, Wire Transfer\n\n"
            "━━━━━━━━━━━━\n\n"
            "🛡️ <b>COMPREHENSIVE BUYER GUARANTEE:</b>\n\n"
            "📦 <b>100% Guaranteed Delivery &amp; DDP Customs</b>\n"
            "All customs clearance, import tariffs, and duties are entirely handled and prepaid by the vendor (Delivered Duty Paid). Zero surprise fees for the recipient.\n\n"
            "🔄 <b>Full Reship Policy</b>\n"
            "In the rare event of transit damage, loss, or customs seizure, your entire order is reshipped immediately free of charge at the vendor’s expense.\n\n"
            "🧪 <b>Blind Lab Testing &amp; Quality Shield</b>\n"
            "Every batch is produced under strict cGMP compliance. If an independent test from an accredited, internationally recognized 3rd-party laboratory (such as Janoshik or equivalent ISO 17025 accredited facility) reveals sub-standard purity (&lt;98%) or incorrect quantity:\n"
            "• 100% refund of the full product value\n"
            "• 100% direct reimbursement of the testing laboratory fee"
        ),
        "chat_card": (
            "<b>TIDETRON PEPTIDES</b>\n"
            "✅ <b>Verified Vendor</b>\n\n"
            "📍 <b>Warehouse:</b> China &amp; USA\n"
            "🚚 <b>Shipping:</b> 10–15 days (China) · 3–5 days (USA)\n"
            "💳 <b>Payment:</b> Alibaba, PayPal, Apple Pay, Crypto &amp; more"
        )
    }
}

buyer_topics = {}
topic_buyers = {}
topic_vendors = {}
buyer_active_vendor = {}
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

def is_admin(user: types.User) -> bool:
    if not user:
        return False
    if user.id in ADMIN_IDS:
        return True
    if user.username and user.username.lower() in ADMIN_USERNAMES:
        return True
    return False

def vendor_list_keyboard():
    buttons = []
    for key, data in VENDORS.items():
        buttons.append([InlineKeyboardButton(text=f"✅ {data['chat_name']}", callback_data=f"open_vendor:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data=f"yes:{key}")],
        [InlineKeyboardButton(text="✏️ Change something", callback_data=f"no:{key}")],
    ])

def make_offer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Make offer", callback_data="start_make_offer")]
    ])

def public_vendor_keyboard(vendor_key: str):
    v = VENDORS.get(vendor_key, {})
    label = v.get("button_text", "💬 Chat with Vendor 🟢")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=label,
            url=f"https://t.me/TrustedPeptideVendorsBot?start={vendor_key}"
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
                    "topic_vendors": topic_vendors,
                    "buyer_active_vendor": buyer_active_vendor,
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
    global group_id, buyer_topics, topic_buyers, topic_vendors, buyer_active_vendor, buyer_names
    global pending, locked_offers, next_offer_number, proof_topic_id
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        group_id = data.get("group_id") or GROUP_ID
        buyer_topics = {int(k): v for k, v in data.get("buyer_topics", {}).items()}
        topic_buyers = {int(k): v for k, v in data.get("topic_buyers", {}).items()}
        topic_vendors = {int(k): v for k, v in data.get("topic_vendors", {}).items()}
        buyer_active_vendor = {int(k): v for k, v in data.get("buyer_active_vendor", {}).items()}
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

async def send_vendor_welcome(message: types.Message, vendor_key: str):
    v = VENDORS.get(vendor_key)
    if not v:
        return
    buyer_active_vendor[message.chat.id] = vendor_key
    save_data()

    await message.answer(v["chat_card"], parse_mode="HTML")

    if os.path.exists(v["banner_path"]):
        await message.answer_photo(FSInputFile(v["banner_path"]))

    if os.path.exists(v["catalog_path"]):
        await message.answer_document(
            FSInputFile(v["catalog_path"]),
            caption="💰 <b>Full Price List</b>",
            parse_mode="HTML",
        )
    await message.answer(
        "💬 <b>Continue with the vendor.</b>\n\n"
        "Just write your message here.",
        parse_mode="HTML"
    )

async def proof_thread(sales_group_id):
    global proof_topic_id
    if proof_topic_id:
        return proof_topic_id
    topic = await bot.create_forum_topic(sales_group_id, "Locked offers")
    proof_topic_id = topic.message_thread_id
    save_data()
    return proof_topic_id

async def clear_lock_button(chat_id, thread_id):
    message_id = lock_button_ids.pop(thread_id, None)
    if message_id:
        try:
            await bot.delete_message(chat_id, message_id)
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
    arg = (command.args or "").lower()
    if arg in VENDORS:
        await send_vendor_welcome(message, arg)
        return
    await message.answer(
        "🛡️ <b>Verified Vendors</b>\n\nChoose a vendor below to start chatting directly:",
        reply_markup=vendor_list_keyboard(),
        parse_mode="HTML",
    )

@dp.callback_query(F.data.startswith("open_vendor:"))
async def open_vendor_callback(callback: types.CallbackQuery):
    await callback.answer()
    vendor_key = callback.data.split(":", 1)[1]
    await send_vendor_welcome(callback.message, vendor_key)

@dp.message(Command("post_directory_info"))
async def post_directory_info_handler(message: types.Message):
    if not is_admin(message.from_user):
        return
    
    text = (
        "🛡️ <b>VERIFIED VENDORS DIRECTORY</b>\n\n"
        "Here you will find rigorously vetted and continuously monitored peptide manufacturers. Every supplier listed meets our strict standards for quality, reliability, and secure fulfillment.\n\n"
        "━━━━━━━━━━━━\n\n"
        "📌 <b>HOW TO GET STARTED:</b>\n\n"
        "<b>1️⃣ Select a Vendor</b>\n"
        "Browse our verified partners below and review their capabilities and terms.\n\n"
        "<b>2️⃣ Open Direct Chat</b>\n"
        "Tap the button beneath each vendor profile to launch an official, secure session.\n\n"
        "<b>3️⃣ Review Catalog &amp; Policies</b>\n"
        "Receive the complete batch price list, warehouse stock, and delivery guidelines automatically.\n\n"
        "<b>4️⃣ Inquire &amp; Order</b>\n"
        "Discuss orders, confirm custom quantities, and complete transactions directly with the vendor team.\n\n"
        "━━━━━━━━━━━━\n\n"
        "🔒 <i>Zero-compromise vetting. Only manufacturers maintaining an unblemished track record and verified lab compliance are listed here.</i>"
    )
    try:
        await bot.send_message(
            message.chat.id,
            text,
            message_thread_id=message.message_thread_id,
            parse_mode="HTML"
        )
    except Exception as e:
        print("Error sending directory info:", e)
    
    try:
        await message.delete()
    except Exception:
        pass

@dp.message(Command("post_vendor"))
async def post_vendor_card(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user):
        return
    
    vendor_key = (command.args or "tidetron").strip().lower()
    v = VENDORS.get(vendor_key)
    if not v:
        await message.reply(f"Vendor '{vendor_key}' not found.")
        return

    banner_file = v["banner_path"]
    thread_id = message.message_thread_id

    try:
        if os.path.exists(banner_file):
            await bot.send_photo(
                message.chat.id,
                FSInputFile(banner_file),
                caption=v["image_caption"],
                parse_mode="HTML",
                message_thread_id=thread_id
            )
        
        await bot.send_message(
            message.chat.id,
            v["post_details"],
            reply_markup=public_vendor_keyboard(vendor_key),
            parse_mode="HTML",
            message_thread_id=thread_id
        )
    except Exception as e:
        print("Error posting vendor card:", e)
        await message.reply(f"Failed to post card: {e}")

    try:
        await message.delete()
    except Exception:
        pass

@dp.message(Command("connect"))
async def connect_topic(message: types.Message):
    global pending_connect_thread
    if message.chat.type == "private":
        return
    if not is_admin(message.from_user):
        return
    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        await message.answer("Open the buyer topic and write /connect there.")
        return
    pending_connect_thread = thread_id
    await message.answer("Waiting for the buyer.\n\nThe buyer must send any message to the bot.\nThen write the offer in this topic.")

@dp.callback_query(F.data == "start_make_offer")
async def make_offer_clicked(callback: types.CallbackQuery):
    await callback.answer()
    thread_id = callback.message.message_thread_id
    if not thread_id or thread_id not in topic_buyers:
        return
    
    waiting_offer_text[thread_id] = True
    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(
        callback.message.chat.id,
        "✍️ <b>Step 1/2: Write the full offer text</b>\n"
        "Include items, quantities, and delivery notes.\n\n"
        "请在此写下完整的报价明细（产品、数量、地址等）：",
        message_thread_id=thread_id,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("yes:"))
async def confirm_offer(callback: types.CallbackQuery):
    global next_offer_number
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or callback.from_user.id != offer.get("buyer_id") or offer.get("status") != "waiting":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return

    await callback.answer("Confirmed")
    code = f"TPVH-{next_offer_number}"
    next_offer_number += 1
    total = float(offer["total"])
    commission = commission_of(total)
    offer["status"] = "locked"
    offer["code"] = code
    locked_offers.append({
        "code": code,
        "total": total,
        "commission": commission,
        "buyer_id": offer["buyer_id"],
        "text": offer["text"],
    })
    save_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Offer {code} is confirmed.\n\n{buyer_offer_text(offer)}\n\nThis is the final offer.")
    
    sales_chat_id = offer.get("chat_id", GROUP_ID)
    await bot.send_message(
        sales_chat_id,
        f"Locked.\n\nOffer: {code}\nTotal: {money(total)}\nCommission due: {money(commission)}\n\nThe buyer does not see the commission.",
        message_thread_id=offer["thread_id"],
    )
    try:
        thread = await proof_thread(sales_chat_id)
        who = buyer_names.get(offer["buyer_id"], "Unknown buyer")
        vendor_name = VENDORS.get(offer.get("vendor_key", "tidetron"), {}).get("chat_name", "Vendor")
        await bot.send_message(
            sales_chat_id,
            f"LOCKED OFFER\n\nOffer: {code}\nVendor: {vendor_name}\nBuyer: {who}\nTotal: {money(total)}\nCommission due: {money(commission)}\n\n{offer['text']}",
            message_thread_id=thread,
        )
    except Exception:
        pass

@dp.callback_query(F.data.startswith("no:"))
async def change_offer(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or callback.from_user.id != offer.get("buyer_id") or offer.get("status") != "waiting":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return
    await callback.answer("Nothing was saved")
    offer["status"] = "changed"
    save_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Nothing was saved. Write what you want to change.")
    target_chat = offer.get("chat_id", GROUP_ID)
    await bot.send_message(target_chat, "The buyer wants a change. Nothing was saved.", message_thread_id=offer["thread_id"])

@dp.message(F.chat.type.in_({"group", "supergroup"}), ~F.text.startswith("/"))
async def from_group_media_and_text(message: types.Message):
    if message.from_user and message.from_user.is_bot:
        return

    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        return
    if thread_id not in topic_buyers:
        return

    buyer_id = topic_buyers[thread_id]
    vendor_key = topic_vendors.get(thread_id, "tidetron")
    caption_text = message.caption or message.text or ""

    if waiting_offer_text.get(thread_id):
        waiting_offer_text.pop(thread_id, None)
        
        if leaks_commission(caption_text):
            await message.reply("Do not write the commission in the offer. Send it again.")
            return

        detected = detect_total(caption_text)
        replace_open_offers(buyer_id)
        key = secrets.token_hex(4)
        pending[key] = {
            "status": "need_total",
            "text": caption_text,
            "total": None,
            "buyer_id": buyer_id,
            "thread_id": thread_id,
            "chat_id": message.chat.id,
            "vendor_key": vendor_key
        }
        waiting_total[thread_id] = key
        save_data()

        hint = f" (detected: {money(detected)})" if detected else ""
        await bot.send_message(
            message.chat.id,
            f"💰 <b>Step 2/2: Confirm the Total Amount</b>{hint}\n"
            "Please type the final total amount now (e.g. 150 or $150):\n\n"
            "请确认最终总金额（例如输入：150 或 $150）：",
            message_thread_id=thread_id,
            parse_mode="HTML"
        )
        return

    waiting_key = waiting_total.get(thread_id)
    if waiting_key and message.text:
        total = parse_only_number(message.text)
        offer = pending.get(waiting_key)
        if total is not None and offer and offer.get("status") == "need_total":
            waiting_total.pop(thread_id, None)
            offer["total"] = total
            await send_confirm_card(waiting_key, offer)
            await message.answer(f"✅ Formal offer sent to buyer for confirmation.\nTotal: {money(total)}")
            return
        else:
            await message.reply("Please write a valid number (e.g. 150 or $150).\n请输入有效金额数字：")
            return

    if leaks_commission(caption_text):
        await message.reply("Do not write the commission in the message.")
        return

    vendor_name = VENDORS.get(vendor_key, {}).get("chat_name", "Vendor")
    header = f"{vendor_name}:\n\n"
    try:
        if message.photo:
            await bot.send_photo(
                buyer_id,
                message.photo[-1].file_id,
                caption=f"{header}{message.caption}" if message.caption else None
            )
        elif message.document:
            await bot.send_document(
                buyer_id,
                message.document.file_id,
                caption=f"{header}{message.caption}" if message.caption else None
            )
        elif message.text:
            await bot.send_message(buyer_id, f"{header}{message.text}")
    except Exception:
        await message.reply("The message was not delivered to the buyer.")
        return

    await clear_lock_button(message.chat.id, thread_id)
    sent = await bot.send_message(
        message.chat.id,
        "Create an official offer card?\n创建正式报价单？",
        message_thread_id=thread_id,
        reply_markup=make_offer_keyboard(),
    )
    lock_button_ids[thread_id] = sent.message_id

@dp.message(F.chat.type == "private")
async def from_buyer_media_and_text(message: types.Message):
    global pending_connect_thread
    if message.text and message.text.startswith("/"):
        return
    if is_admin(message.from_user):
        return

    buyer_id = message.from_user.id
    buyer_names[buyer_id] = buyer_label(message.from_user)

    vendor_key = buyer_active_vendor.get(buyer_id, "tidetron")
    v = VENDORS.get(vendor_key, VENDORS["tidetron"])
    target_group_id = v["sales_group_id"]

    if pending_connect_thread:
        thread_id = pending_connect_thread
        pending_connect_thread = None
        buyer_topics[buyer_id] = thread_id
        topic_buyers[thread_id] = buyer_id
        topic_vendors[thread_id] = vendor_key
        save_data()
        await bot.send_message(target_group_id, "Linked.\nWrite the offer in this topic.", message_thread_id=thread_id)

    thread_id = buyer_topics.get(buyer_id)
    if not thread_id:
        try:
            topic = await bot.create_forum_topic(target_group_id, topic_name(message.from_user))
            thread_id = topic.message_thread_id
            buyer_topics[buyer_id] = thread_id
            topic_buyers[thread_id] = buyer_id
            topic_vendors[thread_id] = vendor_key
            save_data()
            await bot.send_message(
                target_group_id,
                f"New buyer for {v['chat_name']}: {buyer_label(message.from_user)}\nWrite here.",
                message_thread_id=thread_id
            )
        except Exception as e:
            print("Create topic failed:", e)
            await message.answer("Vendor chat not ready. Please try again.")
            return

    save_data()

    if message.photo:
        await bot.send_photo(target_group_id, message.photo[-1].file_id, caption=message.caption, message_thread_id=thread_id)
    elif message.document:
        await bot.send_document(target_group_id, message.document.file_id, caption=message.caption, message_thread_id=thread_id)
    elif message.text:
        await bot.send_message(target_group_id, message.text, message_thread_id=thread_id)

async def main():
    load_data()
    print("Multi-Vendor Bot started successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
