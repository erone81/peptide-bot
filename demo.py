from __future__ import annotations
import asyncio
from contextlib import suppress
from html import escape
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name="demo")

# --- КОНФИГУРАЦИЯ ---
DEMO_VENDOR = "NovaTech Solutions" 
CONTACT_URL = "https://t.me/g3orgel" 
COMMISSION_PCT = 10
TICKET = "#1042"

SERVICES = {
    "pep": ("🧪", "Peptides (B2B Bulk)"),
    "eqp": ("⚙️", "Lab Equipment"),
    "con": ("📝", "Custom Synthesis"),
}
DATES = {"asap": "ASAP", "month": "Within 30 days", "flex": "Flexible"}
BUDGETS = {"s": ("$500–1k", 800), "m": ("$1k–5k", 3500), "l": ("$5k+", 6000)}
OFFERS = {
    "pep": ("Premium Bulk Package", ["cGMP compliant batches", "3rd-party Janoshik testing", "DDP Customs clearance included"]),
    "eqp": ("Turnkey Lab Setup", ["Installation included", "1-year warranty", "24/7 technical support"]),
    "con": ("Custom Formulation", ["Dedicated project manager", "Weekly progress reports", "IP protection guaranteed"]),
}

def money(n: int) -> str:
    return f"${n:,}"

def magic(title: str, body: str) -> str:
    return f"🪄 <b>Behind the scenes · {title}</b>\n\n{body}"

def kb(*rows):
    inline_kb = []
    for row in rows:
        kb_row = []
        for text, data in row:
            if data.startswith("http"):
                kb_row.append(InlineKeyboardButton(text=text, url=data))
            else:
                kb_row.append(InlineKeyboardButton(text=text, callback_data=data))
        inline_kb.append(kb_row)
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

async def pause(bot: Bot, chat_id: int, seconds: float):
    with suppress(Exception):
        await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(seconds)

async def progress(bot: Bot, chat_id: int, stages: list[str]) -> Message:
    n = len(stages)
    status_msg = await bot.send_message(chat_id, f"{'▱' * n}  {stages[0]}", parse_mode="HTML")
    for i, stage in enumerate(stages, 1):
        await asyncio.sleep(0.9)
        with suppress(Exception):
            await status_msg.edit_text(f"{'▰' * i}{'▱' * (n - i)}  {stage}", parse_mode="HTML")
    await asyncio.sleep(0.6)
    return status_msg

async def mark(cb: CallbackQuery, label: str):
    try:
        m = cb.message
        if not m: return
        base_text = m.html_text if hasattr(m, 'html_text') and m.html_text else (m.text or "")
        text = f"{base_text}\n\n▸ <b>{label}</b>"
        with suppress(Exception):
            if m.caption: 
                await m.edit_caption(caption=text, reply_markup=None, parse_mode="HTML")
            else: 
                await m.edit_text(text, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

def _pdf_bytes(title: str, lines: list[str]) -> bytes:
    def esc(s: str) -> bytes: return s.encode("cp1252", "replace").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    ops = [b"BT", b"/F1 24 Tf", b"60 770 Td", b"30 TL", b"(" + esc(title) + b") Tj", b"/F1 12 Tf", b"T*"]
    for line in lines: ops += [b"T*", b"(" + esc(line) + b") Tj"]
    ops.append(b"ET")
    content = b"\n".join(ops)
    bodies = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>", b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(bodies, 1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(bodies) + 1)
    for o in offsets: pdf += b"%010d 00000 n \n" % o
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(bodies) + 1, xref)
    return bytes(pdf)

# --- ТОВА Е ФУНКЦИЯТА, КОЯТО main.py ОЧАКВА ---
async def run_intro(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "✨ <b>DEMO MODE</b> ✨", parse_mode="HTML")
    await pause(bot, chat_id, 1.4)
    await bot.send_message(
        chat_id,
        "<b>Imagine every inquiry arriving like this…</b> 👇\n\n"
        "In the next <b>60 seconds</b> you'll live a complete client journey, from first hello to a paid deal.\n"
        "At every step, I'll show you what happens <i>inside your vendor group</i> at the same moment.\n\n"
        "🎭 <b>You</b> = your future client\n"
        "🪄 <b>Me</b> = your 24/7 automated sales assistant\n\n"
        "<i>No setup. No signup. Just tap.</i>",
        reply_markup=kb([("🎬 Start the tour", "demo_begin")], [("⏭ Skip to the summary", "demo_finale")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_restart")
async def on_restart(cb: CallbackQuery) -> None:
    await cb.answer()
    await run_intro(cb.message.bot, cb.message.chat.id)

@router.callback_query(F.data == "demo_begin")
async def on_begin(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "🎬 Let's go!")
    await pause(cb.message.bot, cb.message.chat.id, 1.5)
    
    svc_buttons = [[(f"{e} {n}", f"demo_svc:{code}")] for code, (e, n) in SERVICES.items()]
    await cb.message.answer(
        "🎭 <b>Step 1/4 · You're the client now</b>\n\n"
        f"You tapped a link on <b>{DEMO_VENDOR}</b>'s channel. "
        "No website, no contact form, no waiting.\n\n"
        "👋 <b>Hi! What are you looking for?</b>",
        reply_markup=kb(*svc_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_svc:"))
async def on_service(cb: CallbackQuery) -> None:
    await cb.answer()
    s = cb.data.split(":")[1]
    e, n = SERVICES[s]
    await mark(cb, f"{e} {n}")
    await pause(cb.message.bot, cb.message.chat.id, 1.3)
    
    date_buttons = [[(f"📅 {label}", f"demo_date:{s}:{code}")] for code, label in DATES.items()]
    await cb.message.answer(
        f"Great choice! {e}\n\n📅 <b>When do you need it?</b>",
        reply_markup=kb(*date_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_date:"))
async def on_date(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    s, d = parts[1], parts[2]
    await mark(cb, f"📅 {DATES[d]}")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    bud_buttons = [[(f"💰 {label}", f"demo_bud:{s}:{d}:{code}")] for code, (label, _) in BUDGETS.items()]
    await cb.message.answer(
        "💰 <b>And your approximate budget?</b>\n<i>Just a rough range, it helps tailor the offer.</i>",
        reply_markup=kb(*bud_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_bud:"))
async def on_budget(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    s, d, b = parts[1], parts[2], parts[3]
    e, n = SERVICES[s]
    blabel, _ = BUDGETS[b]
    name = escape(cb.from_user.full_name)
    username = f"@{escape(cb.from_user.username)}" if cb.from_user.username else "no username"

    await mark(cb, f"💰 {blabel}")
    await pause(cb.message.bot, cb.message.chat.id, 1.0)
    prog = await progress(cb.message.bot, cb.message.chat.id, ["Packing your request…", "Opening your private chat…", f"Notifying {DEMO_VENDOR}…"])
    with suppress(Exception):
        await prog.edit_text("✅ <b>Request sent!</b>\n\n" f"{DEMO_VENDOR} usually replies within minutes. I'll message you here the second they do. 🔔", parse_mode="HTML")
    await asyncio.sleep(2.2)

    await cb.message.answer(
        magic(
            "your vendor group",
            "In that very second, a new <b>Forum Topic</b> appeared in your private vendor group:\n\n"
            "<blockquote>"
            f"🧵 <b>{TICKET} · {name}</b>  🆕\n"
            f"{e} {n}\n"
            f"📅 {DATES[d]}   💰 {blabel}\n"
            f"👤 {username}   ·   first contact"
            "</blockquote>\n"
            "🗂 <b>One client = one topic.</b> Full history, zero scrolling, zero mixed-up chats.\n"
            "🔔 You get notified instantly.\n"
            "👥 You just type naturally to reply.",
        ),
        parse_mode="HTML"
    )
    await asyncio.sleep(2.5)
    await cb.message.answer(
        "Now flip the script. 🔄\nYou're the vendor, and the client is waiting…",
        reply_markup=kb([("💼 Reply as the vendor", f"demo_offer:{s}:{d}:{b}")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_offer:"))
async def on_offer(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    s, d, b = parts[1], parts[2], parts[3]
    _, price = BUDGETS[b]
    title, bullets = OFFERS[s]
    name = escape(cb.from_user.first_name)

    await mark(cb, "💼 Switching to the vendor's seat")
    await cb.message.answer(
        "🎬 <b>Step 2/4 · The vendor's move</b>\n\n"
        "Inside the topic, you simply tap the pinned <b>📝 Make offer</b> button, type the details, and hit Send.\n"
        f"<i>{DEMO_VENDOR} is typing…</i>",
        parse_mode="HTML"
    )
    await pause(cb.message.bot, cb.message.chat.id, 3.8)

    caption = (
        f"✨ <b>Official Offer for {name}</b>\n"
        f"<b>{DEMO_VENDOR}</b> · ✔️ Verified\n"
        "━━━━━━━━━━━━━━━\n"
        f"📦 <b>{title}</b>\n"
        + "\n".join(f"  ✅ {x}" for x in bullets)
        + "\n━━━━━━━━━━━━━━━\n"
        f"💰 <b>Total: {money(price)}</b>"
    )
    markup = kb(
        [("✅ I agree", f"demo_accept:{s}:{d}:{b}")],
        [("💬 Ask a question", "demo_ask")],
    )
    await cb.message.answer(caption, reply_markup=markup, parse_mode="HTML")

    await pause(cb.message.bot, cb.message.chat.id, 1.6)
    pdf = _pdf_bytes(
        f"{DEMO_VENDOR} - Proposal {TICKET}",
        [f"Prepared for: {cb.from_user.full_name}", "",
         f"Package: {title}", *[f"- {x}" for x in bullets], "",
         f"Total: {money(price)}", "",
         "Generated automatically by Trusted Vendors Bot."],
    )
    await cb.message.answer_document(
        BufferedInputFile(pdf, filename=f"Offer-{TICKET[1:]}.pdf"),
        caption="📎 <b>Detailed proposal (PDF)</b>, generated on the fly.",
        parse_mode="HTML"
    )
    await asyncio.sleep(2.0)
    await cb.message.answer(
        magic(
            "what you just did",
            "⚡ <b>A couple of taps</b> produced a branded offer card and a PDF proposal, all delivered inside the client's chat.\n"
            "🏷 Your clients see a polished, verified business, not a random DM.\n"
            "👆 <b>Tap “✅ I agree”</b> on the card above to keep going.",
        ),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_ask")
async def on_ask(cb: CallbackQuery) -> None:
    await cb.answer("💬 In real life this opens a chat. For now, tap “✅ I agree” to continue.", show_alert=True)

@router.callback_query(F.data.startswith("demo_accept:"))
async def on_accept(cb: CallbackQuery) -> None:
    await cb.answer("🎉 Accepted!")
    parts = cb.data.split(":")
    s, d, b = parts[1], parts[2], parts[3]
    _, price = BUDGETS[b]

    await mark(cb, "✅ I agree")
    await pause(cb.message.bot, cb.message.chat.id, 1.5)
    await cb.message.answer(
        "🎬 <b>Step 3/4 · Locking in the deal</b>\n\n"
        "🎉 <b>Wonderful choice!</b>\n"
        f"The total amount is <b>{money(price)}</b>.",
        reply_markup=kb([(f"💳 Mark as Paid (demo)", f"demo_pay:{s}:{d}:{b}")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_pay:"))
async def on_pay(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    b = parts[3]
    _, price = BUDGETS[b]
    fee = price * COMMISSION_PCT // 100
    payout = price - fee
    name = escape(cb.from_user.full_name)

    await mark(cb, "💳 Paying…")
    prog = await progress(cb.message.bot, cb.message.chat.id, ["Processing…", "Issuing receipt…"])
    with suppress(Exception):
        await prog.edit_text(
            "🧾 <b>Payment Confirmed</b>\n\n"
            f"💳 Total: <b>{money(price)}</b>\n"
            f"📌 Order {TICKET} confirmed with <b>{DEMO_VENDOR}</b>\n\n"
            "<i>Thank you for your business!</i>",
            parse_mode="HTML"
        )
    await asyncio.sleep(2.4)

    await cb.message.answer(
        magic(
            "deal closed 🎉",
            "<blockquote>"
            f"🧵 {TICKET} · {name}  →  🟢 <b>PAID</b>"
            "</blockquote>\n"
            f"💰 Deal value: <b>{money(price)}</b>\n"
            f"🏦 Platform Commission ({COMMISSION_PCT}%): <b>{money(fee)}</b>\n"
            f"👛 Your payout: <b>{money(payout)}</b>\n\n"
            "🧮 Everything is tracked. You just click <b>✅ Paid</b> in your group, and the bot handles the accounting.",
        ),
        parse_mode="HTML"
    )
    await asyncio.sleep(3.0)
    await send_finale(cb.message.bot, cb.message.chat.id)

@router.callback_query(F.data == "demo_finale")
async def on_finale(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "⏭ Skipping ahead")
    await send_finale(cb.message.bot, cb.message.chat.id)

async def send_finale(bot: Bot, chat_id: int) -> None:
    await pause(bot, chat_id, 1.5)
    await bot.send_message(
        chat_id,
        "🏁 <b>Step 4/4 · Tour complete!</b>\n\n"
        "Here's what you just experienced:\n\n"
        "✅ A seamless client journey in just a few taps\n"
        "✅ Every inquiry organized in its <b>own Forum Topic</b>\n"
        "✅ Branded <b>offer cards + PDFs</b> without leaving Telegram\n"
        "✅ <b>Commissions tracked automatically</b>\n\n"
        "⏱ <b>Setup takes less than 5 minutes:</b>\n"
        "<blockquote>1️⃣ Add the bot to your group  ·  2️⃣ We generate your link  ·  3️⃣ Done</blockquote>\n"
        "<i>Ready to level up your Telegram sales?</i> 🚀",
        reply_markup=kb(
            [("💬 Contact me to start", CONTACT_URL)],
            [("🔁 Replay the demo", "demo_restart")],
        ),
        parse_mode="HTML"
    )
