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

# --- ДОБАВЕНО ЗА ДЕМОТО ---
from demo import router as demo_router
dp.include_router(demo_router)
# --------------------------

ADMIN_IDS = [8912162282]
ADMIN_USERNAMES = ["g3orgel", "georgel"]

VENDOR_ACCOUNTS = {
    "novapure_li": "novapure",
    "g3orgel": "tidetron",
    "georgel": "tidetron",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/app/data" if os.path.exists("/app/data") else BASE_DIR
DATA_PATH = os.path.join(DATA_DIR, "routes.json")

VENDORS = {
    "tidetron": {
        "name": "1. TIDETRON PEPTIDES",
        "chat_name": "TIDETRON PEPTIDES",
        "sales_group_id": -1004387055068,
        "banner_path": os.path.join(BASE_DIR, "TidetronCatalogCoverHorizontal.jpg"),
        "price_banner_path": os.path.join(BASE_DIR, "TidetronPriceListCover.png"),
        "catalogs": [
            os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf")
        ],
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
    },
    "novapure": {
        "name": "2. NOVAPURE",
        "chat_name": "NOVAPURE",
        "sales_group_id": -1003524946173,
        "banner_path": os.path.join(BASE_DIR, "MainCoverNovapure.jpg"),
        "price_banner_path": os.path.join(BASE_DIR, "NovapurePriceListCover.jpg"),
        "catalogs": [
            os.path.join(BASE_DIR, "Novapure Peptide Product Price List (2026).pdf"),
            os.path.join(BASE_DIR, "NovapureOilPriceList(2026)(3).pdf"),
            os.path.join(BASE_DIR, "Novapure Tablet Product Price List (2026).pdf")
        ],
        "button_text": "💬 Chat with Novapure 🟢",
        "image_caption": (
            "<b>2. NOVAPURE</b>\n"
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
            "<b>NOVAPURE</b>\n"
            "✅ <b>Verified Vendor</b>\n\n"
            "📍 <b>Warehouse:</b> China &amp; USA\n"
            "🚚 <b>Shipping:</b> 10–15 days (China) · 3–5 days (USA)\n"
            "💳 <b>Payment:</b> Alibaba, PayPal, Apple Pay, Crypto &amp; more"
        )
    },
    "handom": {
        "name": "3. HANDOM CHEMICALS",
        "chat_name": "HANDOM CHEMICALS",
        "sales_group_id": -1003218055865,
        "banner_path": os.path.join(BASE_DIR, "HandomChemMainCover.jpg"),
        "price_banner_path": os.path.join(BASE_DIR, "HandomCoverPriceList.jpg"),
        "catalogs": [
            os.path.join(BASE_DIR, "PRICE LIST - PEPTIDES(2026.09.16).pdf")
        ],
        "button_text": "💬 Chat with Handom Chem 🟢",
        "image_caption": (
            "<b>3. HANDOM CHEMICALS</b>\n"
            "✅ <b>Verified Vendor</b>"
        ),
        "post_details": (
            "📍 <b>Warehouse:</b> China\n"
            "🚚 <b>Shipping:</b> 10–15 business days (Global)\n"
            "💳 <b>Payment:</b> Alibaba Trade Assurance, PayPal, Crypto, Wire Transfer\n\n"
            "━━━━━━━━━━━━\n\n"
            "🛡️ <b>COMPREHENSIVE BUYER GUARANTEE:</b>\n\n"
            "📦 <b>100% Guaranteed Delivery &amp; DDP Customs</b>\n"
            "All customs clearance, import tariffs, and duties are entirely handled and prepaid by the vendor (Delivered Duty Paid). Zero surprise fees for the recipient.\n\n"
            "🔄 <b>Full Reship Policy</b>\n"
            "In the rare event of transit damage, loss, or customs seizure, your entire order is reshipped immediately free of charge at the vendor’s expense.\n\n"
            "🧪 <b>Blind Lab Testing &amp; Quality Shield</b>\n"
            "Every batch is produced under strict compliance standards. If an independent test from an accredited, internationally recognized 3rd-party laboratory reveals sub-standard purity (&lt;98%) or incorrect quantity:\n"
            "• 100% refund of the full product value\n"
            "• 100% direct reimbursement of the testing laboratory fee"
        ),
        "chat_card": (
            "<b>HANDOM CHEMICALS</b>\n"
            "✅ <b>Verified Vendor</b>\n\n"
            "📍 <b>Warehouse:</b> China\n"
            "🚚 <b>Shipping:</b> 10–15 days\n"
            "💳 <b>Payment:</b> Alibaba, PayPal, Crypto &amp; more"
        )
    }
}

buyer_topics = {}
topic_buyers = {}
topic_vendors = {}
buyer_active_vendor = {}
buyer_names = {}
buyer_numbers = {}
pending = {}
locked_offers = []
next_offer_number = 1001
next_buyer_number = {}
proof_topic_id = None
waiting_offer_text = {}

def is_admin(user: types.User) -> bool:
    if not user:
        return False
    if user.id in ADMIN_IDS:
        return True
    if user.username and user.username.lower() in ADMIN_USERNAMES:
        return True
    return False

def can_manage_vendor(user: types.User, vendor_key: str) -> bool:
    if is_admin(user):
        return True
    if not user or not user.username:
        return False
    mapped = VENDOR_ACCOUNTS.get(user.username.lower())
    return mapped == vendor_key

def can_view_commission(user: types.User) -> bool:
    if not user:
        return False
    if is_admin(user):
        return True
    if user.username and user.username.lower() in [v.lower() for v in VENDOR_ACCOUNTS.keys()]:
        return True
    return False

def vendor_list_keyboard():
    buttons = []
    for key, data in VENDORS.items():
        buttons.append([InlineKeyboardButton(text=f"✅ {data['chat_name']}", callback_data=f"open_vendor:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_offer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Make offer", callback_data="start_make_offer")]
    ])

def offer_preview_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Send", callback_data=f"offer_send:{key}"),
            InlineKeyboardButton(text="✏ Edit", callback_data=f"offer_edit:{key}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"offer_cancel:{key}")
        ]
    ])

def confirm_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I agree", callback_data=f"yes:{key}")],
    ])

def paid_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Paid", callback_data=f"paid:{key}")]
    ])

def mark_comm_keyboard(code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🟢 Mark Paid ({code})", callback_data=f"mark_paid:{code}")]
    ])

def topic_name(user: types.User, num: int, icon: str = "🆕") -> str:
    who = user.username or user.full_name or "Buyer"
    return f"{icon} #{num} · {who}"[:120]

def money(value):
    return f"{value:.2f} USD"

def commission_of(total):
    return round(float(total) * 0.10, 2)

def clean_number(raw):
    text = (raw or "").strip().replace(" ", "")
    text = re.sub(r"[\$€£]|usd|eur|дол.*|bucks", "", text, flags=re.IGNORECASE).strip()
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

def leaks_commission(text):
    low = (text or "").lower()
    return "commission" in low or "комисион" in low

def buyer_label(user: types.User) -> str:
    username = f"@{user.username}" if user.username else "no username"
    return f"{user.full_name} ({username})"

def save_data():
    try:
        serialized_buyer_topics = {f"{k[0]}_{k[1]}": v for k, v in buyer_topics.items()}
        serialized_buyer_numbers = {f"{k[0]}_{k[1]}": v for k, v in buyer_numbers.items()}

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "buyer_topics": serialized_buyer_topics,
                    "topic_buyers": topic_buyers,
                    "topic_vendors": topic_vendors,
                    "buyer_active_vendor": buyer_active_vendor,
                    "buyer_names": buyer_names,
                    "buyer_numbers": serialized_buyer_numbers,
                    "pending": pending,
                    "locked_offers": locked_offers,
                    "next_offer_number": next_offer_number,
                    "next_buyer_number": next_buyer_number,
                    "proof_topic_id": proof_topic_id,
                },
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global buyer_topics, topic_buyers, topic_vendors, buyer_active_vendor, buyer_names, buyer_numbers
    global pending, locked_offers, next_offer_number, next_buyer_number, proof_topic_id
    
    if not os.path.exists(DATA_PATH):
        return

    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        
        raw_buyer_topics = data.get("buyer_topics", {})
        buyer_topics = {}
        for k, v in raw_buyer_topics.items():
            parts = k.split("_")
            if len(parts) == 2:
                buyer_topics[(int(parts[0]), parts[1])] = v

        topic_buyers = {int(k): v for k, v in data.get("topic_buyers", {}).items()}
        topic_vendors = {int(k): v for k, v in data.get("topic_vendors", {}).items()}
        buyer_active_vendor = {int(k): v for k, v in data.get("buyer_active_vendor", {}).items()}
        buyer_names = {int(k): v for k, v in data.get("buyer_names", {}).items()}

        raw_buyer_numbers = data.get("buyer_numbers", {})
        buyer_numbers = {}
        for k, v in raw_buyer_numbers.items():
            parts = k.split("_")
            if len(parts) == 2:
                buyer_numbers[(int(parts[0]), parts[1])] = v

        pending = data.get("pending", {})
        locked_offers = data.get("locked_offers", [])
        next_offer_number = int(data.get("next_offer_number", 1001))
        
        raw_nbn = data.get("next_buyer_number", 1)
        if isinstance(raw_nbn, int):
            next_buyer_number = {"tidetron": raw_nbn, "novapure": raw_nbn, "handom": raw_nbn}
        else:
            next_buyer_number = raw_nbn

        proof_topic_id = data.get("proof_topic_id")
    except Exception as e:
        print(f"Error loading routes.json: {e}")

async def send_vendor_welcome(message: types.Message, vendor_key: str):
    v = VENDORS.get(vendor_key)
    if not v:
        return
    buyer_active_vendor[message.chat.id] = vendor_key
    save_data()

    await message.answer(v["chat_card"], parse_mode="HTML")

    price_banner = v.get("price_banner_path", v["banner_path"])
    if os.path.exists(price_banner):
        await message.answer_photo(
            FSInputFile(price_banner),
            caption="💎 <b>Official Price List & Catalog</b>",
            parse_mode="HTML"
        )

    catalogs = v.get("catalogs", [])
    for cat_path in catalogs:
        if os.path.exists(cat_path):
            await message.answer_document(
                FSInputFile(cat_path),
                caption="💰 <b>Price List (PDF)</b>",
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

async def update_topic_icon_status(chat_id, thread_id, buyer_id, vendor_key, icon):
    num = buyer_numbers.get((buyer_id, vendor_key), 1)
    who = buyer_names.get(buyer_id, "Buyer")
    new_name = f"{icon} #{num} · {who}"[:120]
    try:
        await bot.edit_forum_topic(chat_id=chat_id, message_thread_id=thread_id, name=new_name)
    except Exception as e:
        print("Failed to update topic icon:", e)

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

@dp.message(Command("commission"))
async def commission_stats(message: types.Message):
    if not can_view_commission(message.from_user):
        return
    
    user_vendor = VENDOR_ACCOUNTS.get(message.from_user.username.lower()) if message.from_user.username else None
    
    if user_vendor and not is_admin(message.from_user):
        filtered_offers = [o for o in locked_offers if o.get("vendor_key") == user_vendor]
        vendor_title = VENDORS.get(user_vendor, {}).get("chat_name", user_vendor.upper())
        header_title = f"📊 <b>COMMISSION &amp; SALES STATS ({vendor_title})</b>"
    else:
        filtered_offers = locked_offers
        header_title = "📊 <b>COMMISSION &amp; SALES STATS (ALL VENDORS)</b>"

    total_sales = sum(o.get("total", 0) for o in filtered_offers)
    total_comm = sum(o.get("commission", 0) for o in filtered_offers)
    unpaid_comm = sum(o.get("commission", 0) for o in filtered_offers if not o.get("paid", False))
    paid_comm = sum(o.get("commission", 0) for o in filtered_offers if o.get("paid", False))
    
    summary = (
        f"{header_title}\n\n"
        f"📦 Total Locked Offers: {len(filtered_offers)}\n"
        f"💰 Total Sales Volume: {money(total_sales)}\n"
        f"💎 Total Commission (10%): {money(total_comm)}\n"
        f"✅ Already Paid: {money(paid_comm)}\n"
        f"⏳ <b>Remaining Due (Unpaid):</b> {money(unpaid_comm)}\n\n"
        f"━━━━━━━━━━━━\n"
        f"📌 <b>UNPAID DEALS BREAKDOWN:</b>"
    )
    
    try:
        await message.answer(summary, parse_mode="HTML", message_thread_id=message.message_thread_id)
    except Exception:
        await message.answer(summary, parse_mode="HTML")

    unpaid_list = [o for o in filtered_offers if not o.get("paid", False)]
    if not unpaid_list:
        await message.answer("🎉 No unpaid commissions! All deals are settled.", message_thread_id=message.message_thread_id)
        return

    admin_user = is_admin(message.from_user)

    for o in unpaid_list:
        code = o.get("code")
        buyer_name = buyer_names.get(o.get("buyer_id"), "Buyer")
        total = o.get("total", 0)
        comm = o.get("commission", 0)
        v_key = o.get("vendor_key", "tidetron")
        v_name = VENDORS.get(v_key, {}).get("chat_name", "")
        
        txt = (
            f"🏷️ <b>Offer:</b> {code} | 🏢 <b>Vendor:</b> {v_name}\n"
            f"👤 <b>Buyer:</b> {buyer_name}\n"
            f"💰 <b>Total:</b> {money(total)} | 💎 <b>Commission:</b> <b>{money(comm)}</b>"
        )
        try:
            if admin_user:
                await message.answer(txt, parse_mode="HTML", message_thread_id=message.message_thread_id, reply_markup=mark_comm_keyboard(code))
            else:
                await message.answer(txt, parse_mode="HTML", message_thread_id=message.message_thread_id)
        except Exception:
            if admin_user:
                await message.answer(txt, parse_mode="HTML", reply_markup=mark_comm_keyboard(code))
            else:
                await message.answer(txt, parse_mode="HTML")

@dp.callback_query(F.data.startswith("mark_paid:"))
async def mark_commission_paid(callback: types.CallbackQuery):
    if not is_admin(callback.from_user):
        await callback.answer("Only the administrator can mark commissions as paid.", show_alert=True)
        return

    code = callback.data.split(":", 1)[1]
    found = False
    for o in locked_offers:
        if o.get("code") == code:
            o["paid"] = True
            found = True
            break
    
    if found:
        save_data()
        await callback.answer(f"Offer {code} commission marked as PAID!")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(f"✅ Commission for offer <b>{code}</b> has been successfully marked as <b>PAID</b>.", parse_mode="HTML")
    else:
        await callback.answer("Offer not found.", show_alert=True)

@dp.callback_query(F.data == "start_make_offer")
async def make_offer_clicked(callback: types.CallbackQuery):
    thread_id = callback.message.message_thread_id
    if not thread_id or thread_id not in topic_buyers:
        await callback.answer("Invalid topic.", show_alert=True)
        return
    
    vendor_key = topic_vendors.get(thread_id, "tidetron")
    if not can_manage_vendor(callback.from_user, vendor_key):
        await callback.answer("⚠️ You are not authorized to create offers for this vendor.", show_alert=True)
        return

    await callback.answer()
    waiting_offer_text[thread_id] = "description"
    await callback.message.answer(
        "✍️ <b>Describe the offer exactly as the client should see it:</b>\n"
        "(Send description as text)",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("offer_send:"))
async def offer_send_callback(callback: types.CallbackQuery):
    global next_offer_number
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or offer.get("status") != "draft":
        await callback.answer("Offer not available.", show_alert=True)
        return

    vendor_key = offer["vendor_key"]
    if not can_manage_vendor(callback.from_user, vendor_key):
        await callback.answer("⚠️ Unauthorized.", show_alert=True)
        return

    code = f"ORD-{next_offer_number}"
    next_offer_number += 1
    total = float(offer["total"])
    
    offer["status"] = "sent"
    offer["code"] = code
    save_data()

    await callback.answer("Offer sent to client!")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(
        f"✅ <b>Offer {code} sent successfully!</b>\n"
        f"Total: {money(total)}",
        parse_mode="HTML"
    )

    buyer_id = offer["buyer_id"]
    sales_chat_id = VENDORS[vendor_key]["sales_group_id"]
    thread_id = offer["thread_id"]
    
    await update_topic_icon_status(sales_chat_id, thread_id, buyer_id, vendor_key, "📦")

    vendor_name = VENDORS.get(vendor_key, {}).get("chat_name", "Vendor")
    card_text = (
        f"<b>Offer {code} from {vendor_name}</b>\n\n"
        f"{offer['description']}\n\n"
        f"<b>Total: {money(total)}</b>\n\n"
        f"Want to change something? Just write to us."
    )
    await bot.send_message(
        buyer_id,
        card_text,
        reply_markup=confirm_keyboard(key),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("offer_edit:"))
async def offer_edit_callback(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer:
        await callback.answer("Draft not found.", show_alert=True)
        return
    if not can_manage_vendor(callback.from_user, offer["vendor_key"]):
        await callback.answer("⚠️ Unauthorized.", show_alert=True)
        return

    thread_id = offer["thread_id"]
    waiting_offer_text[thread_id] = "description"
    pending.pop(key, None)
    save_data()
    await callback.answer("Restarting offer...")
    await callback.message.answer(
        "✍️ <b>Let's start over. Describe the offer:</b>",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("offer_cancel:"))
async def offer_cancel_callback(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if offer:
        if not can_manage_vendor(callback.from_user, offer["vendor_key"]):
            await callback.answer("⚠️ Unauthorized.", show_alert=True)
            return
        offer["status"] = "cancelled"
        save_data()
    await callback.answer("Offer cancelled.")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer("❌ Offer draft cancelled.")

@dp.callback_query(F.data.startswith("yes:"))
async def confirm_offer_buyer(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or callback.from_user.id != offer.get("buyer_id") or offer.get("status") != "sent":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return

    await callback.answer("Confirmed")
    total = float(offer["total"])
    commission = commission_of(total)
    code = offer["code"]
    vendor_key = offer.get("vendor_key", "tidetron")
    
    offer["status"] = "locked"
    
    locked_item = {
        "code": code,
        "total": total,
        "commission": commission,
        "buyer_id": offer["buyer_id"],
        "vendor_key": vendor_key,
        "text": offer["description"],
        "paid": False
    }
    locked_offers.append(locked_item)
    save_data()
    
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
        
    await callback.message.answer(
        f"✅ <b>Offer confirmed!</b>\n\n"
        f"Offer {code} · {money(total)}\n\n"
        f"Thank you!",
        parse_mode="HTML"
    )

    buyer_id = offer["buyer_id"]
    await bot.send_message(buyer_id, "Offer confirmed.")
    
    sales_chat_id = offer.get("chat_id")
    thread_id = offer["thread_id"]
    
    await update_topic_icon_status(sales_chat_id, thread_id, buyer_id, vendor_key, "🔒")

    await bot.send_message(
        sales_chat_id,
        f"🔒 <b>{code} confirmed · {money(total)}</b>\n"
        f"Send the payment link or details to the client here in this topic.",
        message_thread_id=thread_id,
        reply_markup=paid_keyboard(key),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("paid:"))
async def mark_offer_paid(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or offer.get("status") != "locked":
        await callback.answer("Offer not locked or already processed.", show_alert=True)
        return

    vendor_key = offer.get("vendor_key", "tidetron")
    if not can_manage_vendor(callback.from_user, vendor_key):
        await callback.answer("⚠️ You are not authorized to mark this deal as paid.", show_alert=True)
        return

    code = offer.get("code")
    total = float(offer["total"])
    commission = commission_of(total)

    offer["status"] = "completed"
    
    for lo in locked_offers:
        if lo.get("code") == code:
            lo["completed"] = True
            break

    save_data()
    await callback.answer("Deal completed!")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    await callback.message.answer(
        f"✅ <b>MARKED AS PAID & COMPLETED</b>\n"
        f"Offer: {code}\nTotal: {money(total)}",
        parse_mode="HTML"
    )

    buyer_id = offer["buyer_id"]
    sales_chat_id = VENDORS[vendor_key]["sales_group_id"]
    thread_id = offer["thread_id"]

    await update_topic_icon_status(sales_chat_id, thread_id, buyer_id, vendor_key, "🟢")

    await bot.send_message(buyer_id, "Payment confirmed. Thank you!")

    try:
        thread = await proof_thread(sales_chat_id)
        who = buyer_names.get(buyer_id, "Unknown buyer")
        vendor_name = VENDORS.get(vendor_key, {}).get("chat_name", "Vendor")
        await bot.send_message(
            sales_chat_id,
            f"🟢 <b>COMPLETED DEAL</b>\n\n"
            f"Offer: {code}\nVendor: {vendor_name}\nBuyer: {who}\n"
            f"Total: {money(total)}\nCommission (10%): {money(commission)}\n\n{offer['description']}",
            message_thread_id=thread,
            parse_mode="HTML"
        )
    except Exception as e:
        print("Error sending to proof thread:", e)

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
    text = message.text or message.caption or ""

    if waiting_offer_text.get(thread_id) == "description":
        if not can_manage_vendor(message.from_user, vendor_key):
            await message.reply("⚠️ You are not authorized to create offers.")
            return
        if leaks_commission(text):
            await message.reply("Do not write commission in the offer.")
            return
        
        waiting_offer_text[thread_id] = {"desc": text}
        await message.answer(
            "💰 <b>Total amount in USD? Numbers only.</b>\n"
            "(For example: 350 or 350.50)",
            parse_mode="HTML"
        )
        return

    state_data = waiting_offer_text.get(thread_id)
    if isinstance(state_data, dict) and "desc" in state_data and "total" not in state_data:
        if not can_manage_vendor(message.from_user, vendor_key):
            await message.reply("⚠️ You are not authorized.")
            return
        amount = clean_number(text)
        if amount is None:
            await message.reply("Please send a valid number, for example 350 or 350.50.")
            return

        state_data["total"] = amount
        waiting_offer_text.pop(thread_id, None)

        key = secrets.token_hex(4)
        pending[key] = {
            "status": "draft",
            "description": state_data["desc"],
            "total": amount,
            "buyer_id": buyer_id,
            "thread_id": thread_id,
            "chat_id": message.chat.id,
            "vendor_key": vendor_key
        }
        save_data()

        await message.answer(
            f"📋 <b>Offer Preview:</b>\n\n"
            f"{state_data['desc']}\n\n"
            f"<b>Total: {money(amount)}</b>",
            reply_markup=offer_preview_keyboard(key),
            parse_mode="HTML"
        )
        return

    if leaks_commission(text):
        await message.reply("Do not write commission in the message.")
        return

    vendor_name = VENDORS.get(vendor_key, {}).get("chat_name", "Vendor")
    header = f"<b>Отговор от: {vendor_name}</b>\n\n"
    
    try:
        if message.photo:
            await bot.send_photo(buyer_id, message.photo[-1].file_id, caption=f"{header}{message.caption}" if message.caption else header, parse_mode="HTML")
        elif message.document:
            await bot.send_document(buyer_id, message.document.file_id, caption=f"{header}{message.caption}" if message.caption else header, parse_mode="HTML")
        elif message.text:
            await bot.send_message(buyer_id, f"{header}{message.text}", parse_mode="HTML")
    except Exception:
        await message.reply("Failed to deliver message to buyer.")

@dp.message(F.chat.type == "private")
async def from_buyer_media_and_text(message: types.Message):
    if message.text and message.text.startswith("/"):
        return

    buyer_id = message.from_user.id
    buyer_names[buyer_id] = message.from_user.full_name or "Buyer"

    vendor_key = buyer_active_vendor.get(buyer_id, "tidetron")
    v = VENDORS.get(vendor_key, VENDORS["tidetron"])
    target_group_id = v["sales_group_id"]

    topic_key = (buyer_id, vendor_key)
    thread_id = buyer_topics.get(topic_key)

    if not thread_id:
        try:
            if vendor_key not in next_buyer_number:
                next_buyer_number[vendor_key] = 1
            current_num = next_buyer_number[vendor_key]
            next_buyer_number[vendor_key] += 1
            buyer_numbers[topic_key] = current_num
            
            topic = await bot.create_forum_topic(target_group_id, topic_name(message.from_user, current_num, "🆕"))
            thread_id = topic.message_thread_id
            buyer_topics[topic_key] = thread_id
            topic_buyers[thread_id] = buyer_id
            topic_vendors[thread_id] = vendor_key
            save_data()
            
            panel = await bot.send_message(
                target_group_id,
                f"Client #{current_num} for {v['chat_name']}: {buyer_label(message.from_user)}\nUse the button below to send an offer.",
                message_thread_id=thread_id,
                reply_markup=make_offer_keyboard()
            )
            try:
                await bot.pin_chat_message(target_group_id, panel.message_id, disable_notification=True)
            except Exception:
                pass
        except Exception as e:
            print("Create topic failed:", e)
            await message.answer("Vendor chat not ready. Please try again.")
            return

    save_data()

    if message.photo:
        await bot.send_photo(target_group_id, message.photo[-1].file_id, caption=message.caption, message_thread_id=thread_id)
    elif message.document:
        box = message.document
        await bot.send_document(target_group_id, box.file_id, caption=message.caption, message_thread_id=thread_id)
    elif message.text:
        await bot.send_message(target_group_id, message.text, message_thread_id=thread_id)

async def main():
    load_data()
    print("Multi-Vendor Bot started successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
