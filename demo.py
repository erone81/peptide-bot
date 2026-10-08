from __future__ import annotations
import asyncio
from contextlib import suppress
from html import escape
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name="demo")

DEMO_VENDOR = "Novagenix Peptides" 
CONTACT_URL = "https://t.me/g3orgel" 
COMMISSION_PCT = 10
TICKET = "#1042"

def money(n: int) -> str:
    return f"${n:,} USD"

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

# --- ИНТЕРАКТИВНО НАЧАЛО ---
async def run_intro(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "💎 <b>NOVAGENIX PLATFORM · LIVE SIMULATION</b> 💎", parse_mode="HTML")
    await pause(bot, chat_id, 1.2)
    await bot.send_message(
        chat_id,
        "<b>Добре дошъл в интерактивния преглед на реалния процес!</b> 🚀\n\n"
        "Тук ще видиш как софтуерът трансформира хаоса в директните чатове в изпипана B2B екосистема с теми, автоматични оферти, корекции в реално време и проследяване.\n\n"
        "<i>Натисни бутона по-долу, за да стартираме сесията.</i>",
        reply_markup=kb([("🚀 Стартирай симулацията", "demo_step1")]),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"/start demo", "demo"}))
async def demo_text_command(message: Message, bot: Bot) -> None:
    await run_intro(bot, message.chat.id)

# СТЪПКА 1
@router.callback_query(F.data == "demo_step1")
async def step1_vendors(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 1: Избор на вендор")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "👥 <b>[1/10] Меню Verified Vendors в групата</b>\n\n"
        "Клиентът отваря общата група, отива в темата <b>Verified Vendors</b> и вижда списъка с проверени доставчици.\n\n"
        "<blockquote>💡 <i>Системно предимство:</i> Клиентът не губи време из външни сайтове – всичко се случва директно в рамките на Telegram екосистемата.</blockquote>\n\n"
        "<i>Избира да отвори чат с нашия бранд:</i>",
        reply_markup=kb([(f"✅ Chat with {DEMO_VENDOR} 🟢", "demo_step2")]),
        parse_mode="HTML"
    )

# СТЪПКА 2
@router.callback_query(F.data == "demo_step2")
async def step2_welcome(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 2: Прайс лист и запитване")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📄 <b>[2/10] Автоматичен каталог и първи контакт</b>\n\n"
        "Ботът посреща клиента с брандирана карта и му изпраща актуалните ценови листи в PDF.\n\n"
        "💬 <b>Клиентът изпраща първо запитване към вендора:</b>\n"
        "<code>„Здравейте, интересувам се от Ретатрутид 10мг, Тесаморелин 20мг и Мотс-ц 20мг.“</code>",
        reply_markup=kb([("👉 Виж отговора на вендора", "demo_step3")]),
        parse_mode="HTML"
    )

# СТЪПКА 3
@router.callback_query(F.data == "demo_step3")
async def step3_quantities(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 3: Уточняване на бройките")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "💬 <b>[3/10] Уточняване на детайлите в чата</b>\n\n"
        "• <b>Вендорът:</b> <i>„Здравейте! По колко бройки от всеки продукт ще желаете?“</i>\n"
        "• <b>Клиентът:</b> <i>„Моля по 2 бр. от Ретатрутид и Тесаморелин, и 1 бр. от Мотс-ц.“</i>\n"
        "• <b>Вендорът:</b> <i>„Сумата за тези артикули е общо $1,250.“</i>\n"
        "• <b>Клиентът:</b> <i>„Перфектно, цената ме устройва.“</i>\n\n"
        "<blockquote>💡 <i>Задкулисен процес:</i> Дотук комуникацията тече в изолираната тема на клиента в служебната група на вендора, без риск от объркване с други купувачи.</blockquote>",
        reply_markup=kb([("👉 Преминаване към шипинг адрес", "demo_step4")]),
        parse_mode="HTML"
    )

# СТЪПКА 4
@router.callback_query(F.data == "demo_step4")
async def step4_address(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 4: Събиране на данни за доставка")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📦 <b>[4/10] Изискване и получаване на адрес</b>\n\n"
        "• <b>Вендорът:</b> <i>„За да ви подготвя официална поръчка в системата, моля изпратете ми три имена, телефон и точен адрес за доставка.“</i>\n\n"
        "• <b>Клиентът изпраща данните:</b>\n"
        "<code>Григор Петров, тел: +359888123456, гр. Пловдив, ул. Главна 1, ет. 2</code>",
        reply_markup=kb([("👉 Вендорът отваря интерфейса за Make offer", "demo_step5")]),
        parse_mode="HTML"
    )

# СТЪПКА 5
@router.callback_query(F.data == "demo_step5")
async def step5_make_offer(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 5: Оферта, грешка и корекция с Edit")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📝 <b>[5/10] Използване на Make offer и [Edit] бутона</b>\n\n"
        "Вендорът натиска бутона <b>Make offer</b> в темата и попълва бързо поръчката.\n\n"
        "⚠️ <b>Ситуация от практиката:</b> Клиентът пише: <i>„Чакайте, объркал съм една цифра в телефонния номер!“</i>\n"
        "✏️ <b>Решението:</b> Вендорът просто цъка бутона <b>[Edit]</b> на вече създадената оферта, поправя телефона за секунди и я пуска наново без никакво напрежение.",
        reply_markup=kb([("✅ Преглед на коригираната оферта", "demo_step6")]),
        parse_mode="HTML"
    )

# СТЪПКА 6
@router.callback_query(F.data == "demo_step6")
async def step6_proposal(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 6: Официална карта и PDF фактура")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    name = escape(cb.from_user.first_name)
    caption = (
        f"✨ <b>Официална оферта за {name}</b>\n"
        f"<b>{DEMO_VENDOR}</b> · ✅ Verified B2B Supplier\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 <b>Артикули:</b>\n"
        "  • 2x Retatrutide 10mg\n"
        "  • 2x Tesamorelin 20mg\n"
        "  • 1x MOTS-c 20mg\n"
        "📍 <b>Адрес:</b> гр. Пловдив, ул. Главна 1 (Коригиран тел: +359888999888)\n"
        "━━━━━━━━━━━━━━━\n"
        f"💰 <b>Крайна сума: {money(1250)}</b>"
    )
    markup = kb(
        [("✅ Съгласен съм / Потвърди поръчката", "demo_step7")],
        [("💬 Задай въпрос", "demo_ask")],
    )
    await cb.message.answer(caption, reply_markup=markup, parse_mode="HTML")

    pdf = _pdf_bytes(
        f"{DEMO_VENDOR} - Official Order {TICKET}",
        [f"Client: {cb.from_user.full_name}", "Items: 2x Retatrutide, 2x Tesamorelin, 1x MOTS-c", f"Total: {money(1250)}", "Shipping: Plovdiv, Bulgaria (DDP)"],
    )
    await cb.message.answer_document(
        BufferedInputFile(pdf, filename=f"Novagenix-Order-{TICKET[1:]}.pdf"),
        caption="📎 <b>Официална PDF спецификация, генерирана на живо от бота</b>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_ask")
async def on_ask(cb: CallbackQuery) -> None:
    await cb.answer("💬 В реалната платформа тук се отваря директен уточняващ чат.", show_alert=True)

# СТЪПКА 7
@router.callback_query(F.data == "demo_step7")
async def step7_payment(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 7: Плащане и комисионна")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    fee = round(1250 * COMMISSION_PCT / 100, 2)
    
    await cb.message.answer(
        "💳 <b>[7/10] Линк за плащане и отразяване</b>\n\n"
        "• Вендорът изпраща сигурен линк за плащане.\n"
        "• Клиентът плаща и потвърждава в чата: <i>„Готово, платих го!“</i>\n"
        "• Вендорът натиска бутона <b>✅ Paid</b> в служебната тема.\n\n"
        f"<blockquote>💰 <i>Финансов отчет:</i> Платформата автоматично отчита 10% комисионна в размер на <b>${fee} USD</b> към твоя административен панел.</blockquote>",
        reply_markup=kb([("👉 Виж динамиката на иконките в групата", "demo_step8")]),
        parse_mode="HTML"
    )

# СТЪПКА 8
@router.callback_query(F.data == "demo_step8")
async def step8_icons(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 8: Визуален контрол с иконки")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🏷️ <b>[8/10] Динамични статуси на темите в Telegram</b>\n\n"
        "Ето как заглавието на темата в групата се променя автоматично според етапа на поръчката:\n\n"
        "• 🆕 <code>#1042 · Client Name</code> – Нов клиент (входящ лид).\n"
        "• 📦 <code>#1042 · Client Name</code> – Изпратена официална оферта.\n"
        "• 🔒 <code>#1042 · Client Name</code> – Офертата е приета от клиента.\n"
        "• 🟢 <code>#1042 · Client Name</code> – Успешно платено и затворено!\n\n"
        "<i>Пълен контрол само с един поглед върху списъка с теми.</i>",
        reply_markup=kb([("👉 Към тракинга и финалната доставка", "demo_step9")]),
        parse_mode="HTML"
    )

# СТЪПКА 9
@router.callback_query(F.data == "demo_step9")
async def step9_tracking(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 9: Тракинг и клиентска поддръжка")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🚚 <b>[9/10] Изпращане на тракинг и последващи въпроси</b>\n\n"
        "• Вендорът пуска пратката и изпраща тракинг номер в темата: <code>BG987654321</code>\n"
        "• <b>След 3 дни:</b> Клиентът пингва в същия чат: <i>„Здравейте, виждам че пратката е в страната, скоро ли ще е при мен?“</i>\n"
        "• Вендорът отговаря за секунди: <i>„Да, до 24 часа куриерът ще ви я донесе.“</i>",
        reply_markup=kb([("👉 Към финалния акорД", "demo_step10")]),
        parse_mode="HTML"
    )

# СТЪПКА 10
@router.callback_query(F.data == "demo_step10")
async def step10_complete(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Етап 10: Успешен финал")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🎉 <b>[10/10] Успешно пристигане и доволен клиент</b>\n\n"
        "Клиентът получава пратката и пише с усмивка:\n"
        "<b>„Пратката пристигна, всичко е перфектно, много ви благодаря!“</b>\n\n"
        "🪄 <b>Голямата картина:</b> Всичко е подредено, пластено, отчетено и архивирано без нито един изгубен чат или объркан адрес!",
        reply_markup=kb(
            [("💬 Свържи се за интеграция на платформата", CONTACT_URL)],
            [("🔁 Пусни симулацията отново", "demo_restart")],
        ),
        parse_mode="HTML"
    )
