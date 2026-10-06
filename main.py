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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVER_PATH = os.path.join(BASE_DIR, "TidetronCatalogCover.jpg")
CATALOG_PATH = os.path.join(BASE_DIR, "Tidetron Peptide Catalog(3).pdf")
DATA_PATH = os.path.join(BASE_DIR, "routes.json")

VENDOR_USERNAME = "g3orgel"
group_id = None
buyer_topics = {}
topic_buyers = {}
buyer_names = {}
pending = {}
locked_offers = []
next_offer_number = 1001
proof_topic_id = None
lock_button_ids = {}
waiting_total = {}
pending_connect_thread = None

def vendor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tidetron Peptides", callback_data="vendor_tidetron")]
    ])

def confirm_keyboard(key):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data=f"yes:{key}")],
        [InlineKeyboardButton(text="✏️ Change something", callback_data=f"no:{key}")],
    ])

def lock_keyboard(key, total):
    if total:
        text = f"🔒 Lock · {money(total)}"
    else:
        text = "🔒 Lock offer"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"lock:{key}")]
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
    value = float(text)
    if value <= 0:
        return None
    return round(value, 2)

def parse_only_number(text):
    cleaned = (text or "").strip().lower().replace("$", "")
    cleaned = cleaned.replace("usd", "").strip()
    return clean_number(cleaned)

def detect_total(text):
    found = re.findall(
        r"(?i)(?:total|amount|price|合计|总计|总价|金额)\s*[:：]?\s*\$?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
        text or "",
    )
    if not found:
        return None
    return clean_number(found[-1])

def leaks_commission(text):
    low = (text or "").lower()
    return "commission" in low or "комисион" in low

def buyer_label(user: types.User) -> str:
    username = f"@{user.username}" if user.username else "no username"
    return f"{user.full_name} {username}"

def buyer_offer_text(offer):
    text = (offer.get("text") or "").strip()
    detected = detect_total(text)
    if detected is not None and abs(detected - float(offer["total"])) < 0.001:
        return text
    return f"{text}\n\nTotal: {money(offer['total'])}"

def save_data():
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
        )

def load_data():
    global group_id, buyer_topics, topic_buyers, buyer_names
    global pending, locked_offers, next_offer_number, proof_topic_id
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        group_id = data.get("group_id")
        buyer_topics = {int(k): v for k, v in data.get("buyer_topics", {}).items()}
        topic_buyers = {int(k): v for k, v in data.get("topic_buyers", {}).items()}
        buyer_names = {int(k): v for k, v in data.get("buyer_names", {}).items()}
        pending = data.get("pending", {})
        locked_offers = data.get("locked_offers", [])
        next_offer_number = int(data.get("next_offer_number", 1001))
        proof_topic_id = data.get("proof_topic_id")
    except Exception:
        pass

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
    await message.answer_photo(FSInputFile(COVER_PATH))
    await message.answer_document(
        FSInputFile(CATALOG_PATH),
        caption="📄 <b>Full price list</b>",
        parse_mode="HTML",
    )
    await message.answer(
        "💬 Continue with the vendor.\n\nJust write your message here."
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

async def ask_for_total(key, offer):
    offer["status"] = "need_total"
    waiting_total[offer["thread_id"]] = key
    save_data()
    await bot.send_message(
        group_id,
        "Write only the total number.\nExample: 450\n\n只写总价数字。例如：450",
        message_thread_id=offer["thread_id"],
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

@dp.message(Command("connect"))
async def connect_topic(message: types.Message):
    global pending_connect_thread
    if message.chat.type == "private":
        await message.answer("Open the buyer topic in Tidetron Sales TPVH and write /connect there.")
        return
    if (message.from_user.username or "").lower() != VENDOR_USERNAME:
        return
    if group_id is None or message.chat.id != group_id:
        await message.answer("First write /vendor in this group.")
        return
    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        await message.answer("Open the buyer topic and write /connect there.")
        return
    pending_connect_thread = thread_id
    await message.answer(
        "Waiting for the buyer.\n\n"
        "The buyer must send any message to the bot.\n"
        "Then write the offer in this same topic."
    )

@dp.callback_query(F.data.startswith("lock:"))
async def lock_offer(callback: types.CallbackQuery):
    await callback.answer()
    if callback.message.chat.id != group_id:
        return
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer or offer.get("status") != "draft":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return
    if offer.get("total"):
        try:
            await send_confirm_card(key, offer)
        except Exception:
            offer["status"] = "draft"
            save_data()
            await callback.message.answer("The offer was not delivered to the buyer.")
            return
        await callback.message.edit_text(
            f"Sent for confirmation.\nTotal: {money(offer['total'])}"
        )
        return
    await callback.message.edit_text("Waiting for the total number.")
    await ask_for_total(key, offer)

@dp.callback_query(F.data.startswith("yes:"))
async def confirm_offer(callback: types.CallbackQuery):
    global next_offer_number
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer:
        await callback.answer("This offer is no longer active.", show_alert=True)
        return
    if callback.from_user.id != offer.get("buyer_id"):
        await callback.answer("This offer is not for this account.", show_alert=True)
        return
    if offer.get("status") == "replaced":
        await callback.answer("This offer was replaced.", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        return
    if offer.get("status") != "waiting":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return

    await callback.answer("Confirmed")
    code = f"TPVH-{next_offer_number}"
    next_offer_number += 1
    total = float(offer["total"])
    commission = commission_of(total)
    offer["status"] = "locked"
    offer["code"] = code
    locked_offers.append(
        {
            "code": code,
            "total": total,
            "commission": commission,
            "buyer_id": offer["buyer_id"],
            "text": offer["text"],
        }
    )
    save_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Offer {code} is confirmed.\n\n"
        f"{buyer_offer_text(offer)}\n\n"
        "This is the final offer."
    )
    await bot.send_message(
        group_id,
        "Locked.\n\n"
        f"Offer: {code}\n"
        f"Total: {money(total)}\n"
        f"Commission due: {money(commission)}\n\n"
        "The buyer does not see the commission.",
        message_thread_id=offer["thread_id"],
    )
    try:
        thread = await proof_thread()
        who = buyer_names.get(offer["buyer_id"], "Unknown buyer")
        await bot.send_message(
            group_id,
            "LOCKED OFFER\n\n"
            f"Offer: {code}\n"
            "Vendor: Tidetron Peptides\n"
            f"Buyer: {who}\n"
            f"Total: {money(total)}\n"
            f"Commission due: {money(commission)}\n\n"
            f"{offer['text']}",
            message_thread_id=thread,
        )
    except Exception:
        await bot.send_message(
            group_id,
            "The offer is locked, but the proof copy was not posted.",
            message_thread_id=offer["thread_id"],
        )

@dp.callback_query(F.data.startswith("no:"))
async def change_offer(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    offer = pending.get(key)
    if not offer:
        await callback.answer("This offer is no longer active.", show_alert=True)
        return
    if callback.from_user.id != offer.get("buyer_id"):
        await callback.answer("This offer is not for this account.", show_alert=True)
        return
    if offer.get("status") != "waiting":
        await callback.answer("This offer is no longer active.", show_alert=True)
        return
    await callback.answer("Nothing was saved")
    offer["status"] = "changed"
    save_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Nothing was saved. Write what you want to change.")
    await bot.send_message(
        group_id,
        "The buyer wants a change. Nothing was saved.",
        message_thread_id=offer["thread_id"],
    )

@dp.message(F.chat.type.in_({"group", "supergroup"}), F.text, ~F.text.startswith("/"))
async def from_group(message: types.Message):
    if message.from_user and message.from_user.is_bot:
        return
    if group_id is None or message.chat.id != group_id:
        return

    thread_id = message.message_thread_id
    if not thread_id or thread_id == 1:
        await message.reply("Open the buyer topic and write there.")
        return
    if thread_id not in topic_buyers:
        await message.reply(
            "This topic is not linked yet.\n\n"
            "Write /connect here.\n"
            "Then the buyer sends any message to the bot."
        )
        return

    waiting_key = waiting_total.get(thread_id)
    if waiting_key:
        total = parse_only_number(message.text)
        offer = pending.get(waiting_key)
        if total is not None and offer and offer.get("status") == "need_total":
            waiting_total.pop(thread_id, None)
            offer["total"] = total
            try:
                await send_confirm_card(waiting_key, offer)
            except Exception:
                offer["status"] = "need_total"
                waiting_total[thread_id] = waiting_key
                save_data()
                await message.reply("The offer was not delivered to the buyer.")
                return
            await message.answer(f"Sent for confirmation.\nTotal: {money(total)}")
            return
        waiting_total.pop(thread_id, None)
        if offer and offer.get("status") == "need_total":
            offer["status"] = "replaced"

    if leaks_commission(message.text):
        await message.reply("Do not write the commission in the offer. Send it again without that line.")
        return

    buyer_id = topic_buyers[thread_id]
    try:
        await bot.send_message(buyer_id, f"Tidetron Peptides\n\n{message.text}")
    except Exception:
        await message.reply("The message was not delivered.")
        return

    await clear_lock_button(thread_id)
    replace_open_offers(buyer_id)
    total = detect_total(message.text)
    key = secrets.token_hex(4)
    pending[key] = {
        "status": "draft",
        "text": message.text,
        "total": total,
        "buyer_id": buyer_id,
        "thread_id": thread_id,
    }
    save_data()
    sent = await bot.send_message(
        group_id,
        "Final offer?\n最终报价？",
        message_thread_id=thread_id,
        reply_markup=lock_keyboard(key, total),
    )
    lock_button_ids[thread_id] = sent.message_id

@dp.message(F.chat.type == "private", F.text)
async def from_buyer(message: types.Message):
    global pending_connect_thread
    if message.text.startswith("/"):
        return
    if (message.from_user.username or "").lower() == VENDOR_USERNAME:
        await message.answer("Open the Tidetron Sales TPVH group and write in the buyer topic.")
        return
    if not group_id:
        await message.answer("The vendor is not connected yet. Please try again in a minute.")
        return

    buyer_names[message.from_user.id] = buyer_label(message.from_user)

    if pending_connect_thread:
        thread_id = pending_connect_thread
        pending_connect_thread = None
        old = buyer_topics.get(message.from_user.id)
        if old and old in topic_buyers and old != thread_id:
            topic_buyers.pop(old, None)
        buyer_topics[message.from_user.id] = thread_id
        topic_buyers[thread_id] = message.from_user.id
        save_data()
        try:
            await bot.send_message(
                group_id,
                "Linked.\n\nWrite the offer in this topic.",
                message_thread_id=thread_id,
            )
            await bot.send_message(group_id, message.text, message_thread_id=thread_id)
        except Exception:
            await message.answer("The topic could not be linked. Write /connect in the topic again.")
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
        await bot.send_message(
            group_id,
            "New buyer\n"
            f"{buyer_label(message.from_user)}\n\n"
            "Write in this topic. The buyer stays in the same chat.",
            message_thread_id=thread_id,
        )

    save_data()
    await bot.send_message(group_id, message.text, message_thread_id=thread_id)

async def main():
    load_data()
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
