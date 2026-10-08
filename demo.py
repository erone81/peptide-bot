from __future__ import annotations
import asyncio
from contextlib import suppress
from html import escape
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name="demo")

# --- КОНФИГУРАЦИЯ ЗА НАШАТА ПЛАТФОРМА ---
DEMO_VENDOR = "Novagenix Peptides" 
CONTACT_URL = "https://t.me/g3orgel" 
COMMISSION_PCT = 10
TICKET = "#1042"

# Продукти и категории, съобразени с нашия бизнес
PRODUCTS = {
    "bulk": ("🧪", "B2B Bulk Peptides (Vials / Kits)"),
    "blend": ("🧬", "Custom Blends & Solutions"),
    "raw": ("📦", "Raw Material Powder (MOQ 100g+)"),
}

VOLUMES = {
    "v50": "50 – 200 vials",
    "v500": "500+ vials (Wholesale)",
    "kg": "100g+ Raw Powder",
}

DESTINATIONS = {
    "eu": ("🇪🇺", "EU (DDP - No Customs Risk)"),
    "us": ("🇺🇸", "USA Domestic (3-5 days)"),
    "global": ("🌍", "Worldwide Express"),
}

OFFERS_DATA = {
    "bulk": ("Novagenix Wholesale Package", [
        "cGMP certified batch production",
        "3rd-party Janoshik HPLC testing included",
        "100% DDP Customs clearance & guaranteed delivery",
        "Full reshipment protection on transit issues"
    ]),
    "blend": ("Custom Blend Production", [
        "Tailor-made sequences & precise dosing",
        "Strict laboratory quality control",
        "Individually sealed and labeled vials",
        "Full documentation and COA provided"
    ]),
    "raw": ("Raw Material Bulk Supply", [
        "Purity guaranteed ≥98% (Verified)",
        "Discreet double-vacuum sealing",
        "Express air cargo with tracking",
        "Dedicated account manager support"
    ]),
}

def money(n: int) -> str:
    return f"${n:,} USD"

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

# --- НАЧАЛО НА ДЕМОТО ---
async def run_intro(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "✨ <b>NOVAGENIX INTERACTIVE VENDOR DEMO</b> ✨", parse_mode="HTML")
    await pause(bot, chat_id, 1.4)
    await bot.send_message(
        chat_id,
        "<b>Виж как работи нашата B2B платформа за поръчки в реално време…</b> 👇\n\n"
        "В следващите <b>90 секунди</b> ще преминеш през пълния цикъл на една клиентска заявка – от първия контакт до затворената сделка и автоматичното отчитане.\n\n"
        "🎭 <b>Ти</b> = B2B купувач / партньор\n"
        "🪄 <b>Системата</b> = Твоят автоматичен търговски асистент\n\n"
        "<i>Без инсталация. Без формуляри. Само с едно докосване.</i>",
        reply_markup=kb([("🎬 Стартирай демонстрацията", "demo_begin")], [("⏭ Към обобщението", "demo_finale")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_restart")
async def on_restart(cb: CallbackQuery) -> None:
    await cb.answer()
    await run_intro(cb.message.bot, cb.message.chat.id)

@router.callback_query(F.data == "demo_begin")
async def on_begin(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "🎬 Започваме!")
    await pause(cb.message.bot, cb.message.chat.id, 1.5)
    
    prod_buttons = [[(f"{e} {n}", f"demo_prod:{code}")] for code, (e, n) in PRODUCTS.items()]
    await cb.message.answer(
        "📦 <b>Стъпка 1/4 · Избор на продуктов каталог</b>\n\n"
        f"Клиентът кликва върху линк в канала на <b>{DEMO_VENDOR}</b> и веднага отваря директен чат с бота.\n\n"
        "🧪 <b>Какъв тип продуктова категория го интересува?</b>",
        reply_markup=kb(*prod_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_prod:"))
async def on_product(cb: CallbackQuery) -> None:
    await cb.answer()
    prod_key = cb.data.split(":")[1]
    e, n = PRODUCTS[prod_key]
    await mark(cb, f"{e} {n}")
    await pause(cb.message.bot, cb.message.chat.id, 1.3)
    
    vol_buttons = [[(f"📊 {label}", f"demo_vol:{prod_key}:{code}")] for code, label in VOLUMES.items()]
    await cb.message.answer(
        f"Избрано: <b>{n}</b> {e}\n\n"
        "📦 <b>Какъв е приблизителният обем на поръчката?</b>\n"
        "<i>Това помага на екипа ви да подготви точна оферта на едро.</i>",
        reply_markup=kb(*vol_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_vol:"))
async def on_volume(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    prod_key, vol_code = parts[1], parts[2]
    vol_label = VOLUMES[vol_code]
    await mark(cb, f"📊 {vol_label}")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    dest_buttons = [[(f"{e} {label}", f"demo_dest:{prod_key}:{vol_code}:{code}")] for code, (e, label) in DESTINATIONS.items()]
    await cb.message.answer(
        "🌍 <b>Дестинация и логистика:</b>\n"
        "<i>Изберете крайна точка за доставка и митническо обслужване (DDP):</i>",
        reply_markup=kb(*dest_buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_dest:"))
async def on_destination(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    prod_key, vol_code, dest_code = parts[1], parts[2], parts[3]
    e, dest_label = DESTINATIONS[dest_code]
    vol_label = VOLUMES[vol_code]
    _, prod_name = PRODUCTS[prod_key]
    
    name = escape(cb.from_user.full_name)
    username = f"@{escape(cb.from_user.username)}" if cb.from_user.username else "no username"

    await mark(cb, f"{e} {dest_label}")
    await pause(cb.message.bot, cb.message.chat.id, 1.0)
    
    prog = await progress(cb.message.bot, cb.message.chat.id, [
        "Формиране на заявката…",
        "Създаване на изолирана тема (Forum Topic)…",
        f"Нотифициране на екипа на {DEMO_VENDOR}…"
    ])
    
    with suppress(Exception):
        await prog.edit_text(
            "✅ <b>Заявката е изпратена успешно!</b>\n\n"
            f"Екипът на <b>{DEMO_VENDOR}</b> преглежда спецификациите ви и ще ви отговори до минути с официална оферта. 🔔",
            parse_mode="HTML"
        )
    await asyncio.sleep(2.2)

    # Обяснение на бекенд магията за вендора
    await cb.message.answer(
        magic(
            "Какво вижда вендорът в своята група",
            "В същата секунда, в закритата служебна група на вашия бизнес се появява **отделна тема (Forum Topic)**:\n\n"
            "<blockquote>"
            f"🧵 <b>{TICKET} · {name}</b>  🆕\n"
            f"📦 {prod_name}\n"
            f"📊 Обем: {vol_label}   {e} {dest_label}\n"
            f"👤 {username}   ·   B2B лид"
            "</blockquote>\n"
            "🗂 <b>Пълна изолация:</b> Всеки клиент си има собствена тема с цялата история на кореспонденцията.\n"
            "🔔 <b>Моментален известител:</b> Мениджърите ви получават нотификация веднага.\n"
            "👥 <b>Екипна работа:</b> Колегите могат да се включват в темата, без клиентът да разбере.",
        ),
        parse_mode="HTML"
    )
    await asyncio.sleep(2.5)
    await cb.message.answer(
        "🔄 <b>Сега сменяме ролята!</b>\n"
        "Представи си, че си мениджър на Novagenix и клиентът чака официална оферта…",
        reply_markup=kb([("💼 Създай оферта като вендор", f"demo_offer:{prod_key}:{vol_code}:{dest_code}")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_offer:"))
async def on_offer(cb: CallbackQuery) -> None:
    await cb.answer()
    parts = cb.data.split(":")
    prod_key = parts[1]
    title, bullets = OFFERS_DATA[prod_key]
    name = escape(cb.from_user.first_name)
    price = 3850 if prod_key == "bulk" else (5200 if prod_key == "blend" else 4500)

    await mark(cb, "💼 Преминаване към ролята на вендор")
    await cb.message.answer(
        "📋 <b>Стъпка 2/4 · Изготвяне на оферта от вендора</b>\n\n"
        "Вътре в темата мениджърът натиска бутона <b>📝 Make offer</b>, въвежда детайлите и цената в USD.\n"
        f"<i>{DEMO_VENDOR} подготвя предложението…</i>",
        parse_mode="HTML"
    )
    await pause(cb.message.bot, cb.message.chat.id, 3.8)

    caption = (
        f"✨ <b>Официална оферта за {name}</b>\n"
        f"<b>{DEMO_VENDOR}</b> · ✅ Verified B2B Supplier\n"
        "━━━━━━━━━━━━━━━\n"
        f"📦 <b>{title}</b>\n"
        + "\n".join(f"  ✅ {x}" for x in bullets)
        + "\n━━━━━━━━━━━━━━━\n"
        f"💰 <b>Обща сума: {money(price)}</b>"
    )
    markup = kb(
        [("✅ Съгласен съм / Потвърди", f"demo_accept:{price}")],
        [("💬 Задай въпрос", "demo_ask")],
    )
    await cb.message.answer(caption, reply_markup=markup, parse_mode="HTML")

    # Генериране на PDF предложение в паметта
    await pause(cb.message.bot, cb.message.chat.id, 1.6)
    pdf = _pdf_bytes(
        f"{DEMO_VENDOR} - B2B Proposal {TICKET}",
        [f"Prepared for: {cb.from_user.full_name}", "",
         f"Package: {title}", *[f"- {x}" for x in bullets], "",
         f"Total Amount: {money(price)}", "",
         "Certified Quality & DDP Compliance - Novagenix Peptides."],
    )
    await cb.message.answer_document(
        BufferedInputFile(pdf, filename=f"Novagenix-Offer-{TICKET[1:]}.pdf"),
        caption="📎 <b>Официална спецификация и оферта (PDF)</b>, генерирана автоматично.",
        parse_mode="HTML"
    )
    await asyncio.sleep(2.0)
    await cb.message.answer(
        magic(
            "Професионализъм на най-високо ниво",
            "⚡ Ботът автоматично комбинира текстовата оферта, интерактивните бутони и официалния PDF документ в чата на купувача.\n"
            "🏷 Клиентът вижда луксозен брандинг и пълна прозрачност, което драстично вдига процента на затворените сделки.",
        ),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_ask")
async def on_ask(cb: CallbackQuery) -> None:
    await cb.answer("💬 В реалната система това отваря директен диалог в същата тема. За целта на демото, натисни „✅ Съгласен съм“.", show_alert=True)

@router.callback_query(F.data.startswith("demo_accept:"))
async def on_accept(cb: CallbackQuery) -> None:
    await cb.answer("🎉 Поръчката е потвърдена!")
    price = int(cb.data.split(":")[1])

    await mark(cb, "✅ Офертата е приета")
    await pause(cb.message.bot, cb.message.chat.id, 1.5)
    await cb.message.answer(
        "💳 <b>Стъпка 3/4 · Финализиране и плащане</b>\n\n"
        "🎉 <b>Сделката е договорена!</b>\n"
        f"Сума за плащане: <b>{money(price)}</b>.\n"
        "<i>Натисни бутона по-долу за симулиране на плащане от клиента:</i>",
        reply_markup=kb([("💳 Маркирай като платено (Демо)", f"demo_pay:{price}")]),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("demo_pay:"))
async def on_pay(cb: CallbackQuery) -> None:
    await cb.answer()
    price = int(cb.data.split(":")[1])
    fee = round(price * COMMISSION_PCT / 100, 2)
    payout = price - fee
    name = escape(cb.from_user.full_name)

    await mark(cb, "💳 Плащането е отразено")
    prog = await progress(cb.message.bot, cb.message.chat.id, ["Обработка на транзакцията…", "Генериране на отчет за комисионната…"])
    with suppress(Exception):
        await prog.edit_text(
            "🧾 <b>Плащането е потвърдено успешно!</b>\n\n"
            f"💳 Обща сума: <b>{money(price)}</b>\n"
            f"📌 Поръчка {TICKET} е официално затворена с <b>{DEMO_VENDOR}</b>\n\n"
            "<i>Благодарим ви за доверието! Логистиката е стартирана.</i>",
            parse_mode="HTML"
        )
    await asyncio.sleep(2.4)

    # Обяснение на автоматичното отчитане на комисионната
    await cb.message.answer(
        magic(
            "Автоматично счетоводство и комисионни",
            "<blockquote>"
            f"🧵 {TICKET} · {name}  →  🟢 <b>ЗАВЪРШЕНА СДЕЛКА (PAID)</b>"
            "</blockquote>\n"
            f"💰 Общ обем на сделката: <b>{money(price)}</b>\n"
            f"🏦 Платформена комисионна ({COMMISSION_PCT}%): <b>${fee:,.2f} USD</b> (Калкулирана автоматично)\n"
            f"👛 Чист приход за вендора: <b>${payout:,.2f} USD</b>\n\n"
            "🧮 <b>Край на излишните таблици и спорове:</b> Системата сама следи дължимите комисионни, генерира справки с командата `/commission` и показва кой какво дължи в реално време.",
        ),
        parse_mode="HTML"
    )
    await asyncio.sleep(3.0)
    await send_finale(cb.message.bot, cb.message.chat.id)

@router.callback_query(F.data == "demo_finale")
async def on_finale(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "⏭ Към финала")
    await send_finale(cb.message.bot, cb.message.chat.id)

async def send_finale(bot: Bot, chat_id: int) -> None:
    await pause(bot, chat_id, 1.5)
    await bot.send_message(
        chat_id,
        "🏁 <b>Стъпка 4/4 · Демонстрацията завърши успешно!</b>\n\n"
        "Ето какво видя в действие:\n\n"
        "✅ <b>B2B поръчки без сайт и формуляри</b> в рамките на секунди\n"
        "✅ <b>Пълна организация</b> – всеки клиент е в собствена тема (Forum Topic)\n"
        "✅ <b>Професионални оферти и PDF спецификации</b> с едно натискане\n"
        "✅ <b>Автоматично следене на 10% комисионна</b> и финансови отчети\n\n"
        "⏱ <b>Интеграцията отнема по-малко от 5 минути:</b>\n"
        "<blockquote>1️⃣ Добавяш бота в групата  ·  2️⃣ Създаваме твоя линк  ·  3️⃣ Готов си за продажби</blockquote>\n"
        "<i>Готов ли си да пренесеш продажбите на Novagenix на следващото ниво?</i> 🚀",
        reply_markup=kb(
            [("💬 Свържи се с нас за старт", CONTACT_URL)],
            [("🔁 Пусни демото отначало", "demo_restart")],
        ),
        parse_mode="HTML"
    )
