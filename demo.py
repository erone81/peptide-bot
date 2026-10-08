from __future__ import annotations
import asyncio
from contextlib import suppress
from html import escape
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name="demo")

# --- КОНФИГУРАЦИЯ ЗА НИКА И ПЛАТФОРМАТА ---
DEMO_VENDOR = "Novagenix Peptides" 
CONTACT_URL = "https://t.me/g3orgel" 
COMMISSION_PCT = 10
TICKET = "#1042"

# --- ПОМОЩНИ ФУНКЦИИ ---
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

# --- НАЧАЛО НА ИНТЕРАКТИВНОТО ДЕМО ---
async def run_intro(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "✨ <b>NOVAGENIX PLATFORM LIVE DEMO</b> ✨", parse_mode="HTML")
    await pause(bot, chat_id, 1.2)
    await bot.send_message(
        chat_id,
        "<b>Добре дошъл в интерактивната демонстрация на реалния работен процес!</b> 🚀\n\n"
        "Тук ще видиш как клиентът влиза в групата, избира вендор, разменя съобщения, получава оферта с грешка и корекция, плаща и проследява пратката си до финала.\n\n"
        "<i>Натисни бутона по-долу, за да започнем пътешествието из нашата система.</i>",
        reply_markup=kb([("🎬 Влез в групата и стартирай", "demo_step1")]),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"/start demo", "demo"}))
async def demo_text_command(message: Message, bot: Bot) -> None:
    await run_intro(bot, message.chat.id)

# СТЪПКА 1: Избор на вендор от темата Verified Vendors
@router.callback_query(F.data == "demo_step1")
async def step1_vendors(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 1: Избор на вендор")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "👥 <b>Стъпка 1/10 · Меню Verified Vendors в групата</b>\n\n"
        "Клиентът влиза в основната Telegram група, отваря темата <b>Verified Vendors</b> и вижда списъка с проверени доставчици.\n\n"
        "<i>Избира да започне чат с <b> Novagenix Peptides</b>:</i>",
        reply_markup=kb([(f"✅ Chat with {DEMO_VENDOR} 🟢", "demo_step2")]),
        parse_mode="HTML"
    )

# СТЪПКА 2: Получаване на прайс лист и начално запитване
@router.callback_query(F.data == "demo_step2")
async def step2_welcome(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 2: Прайс лист и запитване")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📄 <b>Стъпка 2/10 · Автоматичен прайс лист</b>\n\n"
        "Ботът посприема клиента и му изпраща официалния каталог и ценова листа в PDF формат.\n\n"
        "💬 <b>Клиентът пише първото си запитване към реален човек (вендора):</b>\n"
        "<i>„Здравейте, интересувам се от Ретатрутид 10мг, Тесаморелин 20мг и Мотс-ц 20мг.“</i>",
        reply_markup=kb([("👉 Продължи към отговора на вендора", "demo_step3")]),
        parse_mode="HTML"
    )

# СТЪПКА 3: Уточняване на бройките
@router.callback_query(F.data == "demo_step3")
async def step3_quantities(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 3: Уточняване на количества")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "💬 <b>Стъпка 3/10 · Диалог за бройките</b>\n\n"
        "• <b>Вендорът пита:</b> <i>„Здравейте! По колко бройки от всеки продукт ще желаете?“</i>\n"
        "• <b>Клиентът отговаря:</b> <i>„Моля по 2 броя от Ретатрутид и Тесаморелин, и 1 брой от Мотс-ц.“</i>\n"
        "• <b>Вендорът дава предварителна цена:</b> <i>„Сумата за тези артикули е общо $1,250.“</i>\n"
        "• <b>Клиентът потвърждава:</b> <i>„Перфектно, цената ме устройва.“</i>",
        reply_markup=kb([("👉 Изпращане на адрес за доставка", "demo_step4")]),
        parse_mode="HTML"
    )

# СТЪПКА 4: Събиране на шипинг адрес
@router.callback_query(F.data == "demo_step4")
async def step4_address(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 4: Шипинг адрес")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📦 <b>Стъпка 4/10 · Изискване на шипинг адрес</b>\n\n"
        "• <b>Вендорът пише:</b> <i>„За да ви пусна официална поръчка в системата, моля изпратете ми три имена, телефон и точен адрес за доставка.“</i>\n"
        "• <b>Клиентът изпраща данните:</b>\n"
        "<i>Григор Петров, тел: +359888123456, гр. Пловдив, ул. Главна 1, ет. 2</i>",
        reply_markup=kb([("👉 Вендорът създава Make offer", "demo_step5")]),
        parse_mode="HTML"
    )

# СТЪПКА 5: Make offer с грешка и Edit
@router.callback_query(F.data == "demo_step5")
async def step5_make_offer(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 5: Make offer и корекция")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "📝 <b>Стъпка 5/10 · Бутон Make offer и поправка на грешка</b>\n\n"
        "Вендорът натиска вътрешния бутон <b>Make offer</b>, попълва артикулите (2x Ретатрутид, 2x Тесаморелин, 1x Мотс-ц), адреса и въвежда цена $1,250, след което я изпраща.\n\n"
        "⚠️ <b>Клиентът забелязва грешка:</b> <i>„Чакайте, объркал съм телефонния номер в адреса!“</i>\n"
        "✏️ <b>Вендорът бързо използва бутона [Edit]</b> в системата, коригира телефона и пуска офертата отново за секунди без да губи историята.",
        reply_markup=kb([("✅ Потвърди корекцията и види офертата", "demo_step6")]),
        parse_mode="HTML"
    )

# СТЪПКА 6: Финална оферта и PDF
@router.callback_query(F.data == "demo_step6")
async def step6_proposal(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 6: Официална оферта")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    name = escape(cb.from_user.first_name)
    caption = (
        f"✨ <b>Официална оферта за {name}</b>\n"
        f"<b>{DEMO_VENDOR}</b> · ✅ Verified Supplier\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 <b>Съдържание на поръчката:</b>\n"
        "  • 2x Retatrutide 10mg\n"
        "  • 2x Tesamorelin 20mg\n"
        "  • 1x MOTS-c 20mg\n"
        "📍 <b>Адрес:</b> гр. Пловдив, ул. Главна 1 (Тел: +359888123456)\n"
        "━━━━━━━━━━━━━━━\n"
        f"💰 <b>Крайна сума: {money(1250)}</b>"
    )
    markup = kb(
        [("✅ Съгласен съм / Потвърди поръчката", "demo_step7")],
        [("💬 Задай въпрос", "demo_ask")],
    )
    await cb.message.answer(caption, reply_markup=markup, parse_mode="HTML")

    # Генериране на PDF
    pdf = _pdf_bytes(
        f"{DEMO_VENDOR} - Official Order {TICKET}",
        [f"Client: {cb.from_user.full_name}", "Items: 2x Retatrutide, 2x Tesamorelin, 1x MOTS-c", f"Total: {money(1250)}", "Shipping: Plovdiv, Bulgaria"],
    )
    await cb.message.answer_document(
        BufferedInputFile(pdf, filename=f"Novagenix-Order-{TICKET[1:]}.pdf"),
        caption="📎 <b>Официална PDF фактура и спецификация към поръчката</b>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_ask")
async def on_ask(cb: CallbackQuery) -> None:
    await cb.answer("💬 В реалната система това отваря чат в същата тема.", show_alert=True)

# СТЪПКА 7: Линк за плащане и потвърждение
@router.callback_query(F.data == "demo_step7")
async def step7_payment(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 7: Плащане")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    fee = round(1250 * COMMISSION_PCT / 100, 2)
    
    await cb.message.answer(
        "💳 <b>Стъпка 7/10 · Линк за плащане и потвърждение</b>\n\n"
        "• Вендорът изпраща сигурен линк за плащане.\n"
        "• Клиентът го отваря, извършва плащането и пише в чата: <i>„Готово, платих го!“</i>\n"
        "• Вендорът проверява сметката си и натиска бутона <b>✅ Paid</b> в служебната тема.\n\n"
        f"🏦 <i>Системата автоматично начислява 10% платформена комисионна (${fee} USD) към твоя баланс.</i>",
        reply_markup=kb([("👉 Виж как се променят иконките в групата", "demo_step8")]),
        parse_mode="HTML"
    )

# СТЪПКА 8: Обяснение на иконките и темите
@router.callback_query(F.data == "demo_step8")
async def step8_icons(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 8: Статуси и иконки")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🏷️ <b>Стъпка 8/10 · Магията на иконките и темите в групата</b>\n\n"
        "Ето как системата ти дава пълен визуален контрол в служебната група на вендора:\n\n"
        "• 🆕 <b>#1042 · Client Name</b> – Нова входяща заявка (първи контакт).\n"
        "• 📦 <b>#1042 · Client Name</b> – Изпратена официална оферта към клиента.\n"
        "• 🔒 <b>#1042 · Client Name</b> – Офертата е приета, очаква се плащане.\n"
        "• 🟢 <b>#1042 · Client Name</b> – Сделката е платена и завършена (депозирана в архива за комисионни).\n\n"
        "<i>Така екипът ти никога не губи ориентация кой клиент на какъв етап е!</i>",
        reply_markup=kb([("👉 Продължи към изпращане и тракинг", "demo_step9")]),
        parse_mode="HTML"
    )

# СТЪПКА 9: Тракинг номер и въпроси
@router.callback_query(F.data == "demo_step9")
async def step9_tracking(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 9: Тракинг и доставка")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🚚 <b>Стъпка 9/10 · Тракинг номер и проследяване</b>\n\n"
        "• Вендорът изпраща в темата тракинг номер: <i>„Пратките ви бяха обработени, ето номер за проследяване: BG987654321“</i>\n"
        "• <b>3 дни по-късно:</b> Клиентът пингва вендора в същия чат: <i>„Здравейте, пратката пристигна в страната, виждам че е на митница, скоро ли ще е при мен?“</i>\n"
        "• Вендорът отговаря: <i>„Да, до 24 часа куриерът ще ви я донесе на посочения адрес.“</i>",
        reply_markup=kb([("👉 Финал на процеса", "demo_step10")]),
        parse_mode="HTML"
    )

# СТЪПКА 10: Финал и успешно пристигане
@router.callback_query(F.data == "demo_step10")
async def step10_complete(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 10: Успешен завършек")
    await pause(cb.message.bot, cb.message.chat.id, 1.2)
    
    await cb.message.answer(
        "🎉 <b>Стъпка 10/10 · Финал на поръчката</b>\n\n"
        "• Клиентът получава пратката и пише с усмивка в чата:\n"
        "<b>„Пратката пристигна, всичко е перфектно, много ви благодаря!“</b>\n\n"
        "🪄 <b>Какво постигнахме?</b>\n"
        "Цялата комуникация е кристално организирана в изолирана тема, плащането е отразено, комисионната е засечена, а клиентът е напълно обслужван без напускане на Telegram!",
        reply_markup=kb(
            [("💬 Свържи се с нас за интеграция", CONTACT_URL)],
            [("🔁 Пусни демото отново", "demo_restart")],
        ),
        parse_mode="HTML"
    )
