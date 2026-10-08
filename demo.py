from __future__ import annotations
import asyncio
from contextlib import suppress
from html import escape
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router(name="demo")

DEMO_VENDOR = "Novagenix Peptides" 
CONTACT_URL = "https://t.me/g3orgel" 
COMMISSION_PCT = 10
TICKET = "ORD-1042"

def money(n: int) -> str:
    return f"${n:,.2f} USD"

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

# Анимиран индикатор за зареждане на живо
async def live_animation(bot: Bot, chat_id: int, text: str):
    msg = await bot.send_message(chat_id, f"⏳ <i>{text}</i>", parse_mode="HTML")
    for _ in range(2):
        await asyncio.sleep(0.4)
        with suppress(Exception):
            await msg.edit_text(f"⏳ <i>{text}.</i>", parse_mode="HTML")
        await asyncio.sleep(0.4)
        with suppress(Exception):
            await msg.edit_text(f"⏳ <i>{text}..</i>", parse_mode="HTML")
        await asyncio.sleep(0.4)
        with suppress(Exception):
            await msg.edit_text(f"⏳ <i>{text}...</i>", parse_mode="HTML")
    with suppress(Exception):
        await msg.delete()

# --- СТАРТ НА ДЕМОТО ---
async def run_intro(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "💎 <b>NOVAGENIX PLATFORM · LIVE SIMULATION</b> 💎", parse_mode="HTML")
    await pause(bot, chat_id, 1.0)
    await bot.send_message(
        chat_id,
        "<b>Добре дошъл в интерактивната симулация на реалния работен процес!</b> 🚀\n\n"
        "Тук на живо ще видиш как софтуерът премахва хаоса в чатовете: от избора на вендор, размяната на продукти като <i>Retatrutide</i>, корекциите в реално време, до финансовите отчети с командата <code>/commission</code>.\n\n"
        "<i>Натисни системния бутон по-долу, за да започнем:</i>",
        reply_markup=kb([("▶️ Стартирай симулацията", "demo_step1")]),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"/start demo", "demo"}))
async def demo_text_command(message: Message, bot: Bot) -> None:
    await run_intro(bot, message.chat.id)

# СТЪПКА 1
@router.callback_query(F.data == "demo_step1")
async def step1_vendors(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 1: Избор на вендор")
    await live_animation(cb.message.bot, cb.message.chat.id, "Зареждане на Verified Vendors менюто")
    
    await cb.message.answer(
        "👥 <b>[Етап 1 от 10] Меню Verified Vendors в групата</b>\n\n"
        "Клиентът влиза в основната група, отваря темата <b>Verified Vendors</b> и вижда акредитираните доставчици.\n\n"
        "<blockquote>💡 <i>Системно предимство:</i> Всичко се случва изцяло в Telegram екосистемата, без външни сайтове и излишни кликове.</blockquote>\n\n"
        "<i>Системен бутон в интерфейса:</i>",
        reply_markup=kb([(f"✅ Chat with {DEMO_VENDOR} 🟢", "demo_step2")]),
        parse_mode="HTML"
    )

# СТЪПКА 2
@router.callback_query(F.data == "demo_step2")
async def step2_welcome(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 2: Прайс лист и запитване")
    await live_animation(cb.message.bot, cb.message.chat.id, "Изпращане на продуктов каталог")
    
    await cb.message.answer(
        "📄 <b>[Етап 2 от 10] Автоматичен каталог и запитване</b>\n\n"
        "Ботът изпраща ценовата листа и посреща купувача.\n\n"
        "💬 <b>Реално съобщение от клиента в чата:</b>\n"
        "<code>„Здравейте, интересувам се от Ретатрутид 10мг, Тесаморелин 20мг и Мотс-ц 20мг.“</code>",
        reply_markup=kb([("👉 Продължи към уточняването на бройките", "demo_step3")]),
        parse_mode="HTML"
    )

# СТЪПКА 3
@router.callback_query(F.data == "demo_step3")
async def step3_quantities(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 3: Уточняване на бройки")
    await pause(cb.message.bot, cb.message.chat.id, 0.8)
    
    await cb.message.answer(
        "💬 <b>[Етап 3 от 10] Диалог за бройките и цена</b>\n\n"
        "• <b>Вендорът:</b> <i>„Здравейте! По колко бройки от всеки продукт ще желаете?“</i>\n"
        "• <b>Клиентът:</b> <i>„Моля по 2 бр. от Ретатрутид и Тесаморелин, и 1 бр. от Мотс-ц.“</i>\n"
        "• <b>Вендорът:</b> <i>„Сумата за тези артикули е общо $1,250.“</i>\n"
        "• <b>Клиентът:</b> <i>„Перфектно, цената ме устройва.“</i>",
        reply_markup=kb([("👉 Продължи към шипинг адреса", "demo_step4")]),
        parse_mode="HTML"
    )

# СТЪПКА 4
@router.callback_query(F.data == "demo_step4")
async def step4_address(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 4: Шипинг адрес")
    await pause(cb.message.bot, cb.message.chat.id, 0.8)
    
    await cb.message.answer(
        "📦 <b>[Етап 4 от 10] Събиране на данни за доставка</b>\n\n"
        "• <b>Вендорът:</b> <i>„За да ви пусна официална поръчка в системата, моля изпратете ми три имена, телефон и точен адрес за доставка.“</i>\n\n"
        "• <b>Клиентът изпраща данните:</b>\n"
        "<code>Григор Петров, тел: +359888123456, гр. Пловдив, ул. Главна 1, ет. 2</code>",
        reply_markup=kb([("👉 Вендорът създава Make offer", "demo_step5")]),
        parse_mode="HTML"
    )

# СТЪПКА 5
@router.callback_query(F.data == "demo_step5")
async def step5_make_offer(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 5: Make offer и корекция с Edit")
    await live_animation(cb.message.bot, cb.message.chat.id, "Обработка на поръчката в системата")
    
    await cb.message.answer(
        "📝 <b>[Етап 5 от 10] Използване на Make offer и [Edit] бутона</b>\n\n"
        "Вендорът натиска системния бутон <b>Make offer</b>, попълва артикулите и адреса.\n\n"
        "⚠️ <b>Ситуация:</b> Клиентът пише: <i>„Чакайте, объркал съм една цифра в телефона!“</i>\n"
        "✏️ <b>Решение:</b> Вендорът бързо натиска системния бутон <b>[Edit]</b>, коригира телефона и я пуска наново за секунди.",
        reply_markup=kb([("✅ Преглед на финалната оферта", "demo_step6")]),
        parse_mode="HTML"
    )

# СТЪПКА 6
@router.callback_query(F.data == "demo_step6")
async def step6_proposal(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 6: Официална оферта")
    await pause(cb.message.bot, cb.message.chat.id, 0.8)
    
    name = escape(cb.from_user.first_name)
    caption = (
        f"<b>Offer {TICKET} from {DEMO_VENDOR}</b>\n\n"
        f"✨ <b>Официална оферта за {name}</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 <b>Съдържание:</b>\n"
        "  • 2x Retatrutide 10mg\n"
        "  • 2x Tesamorelin 20mg\n"
        "  • 1x MOTS-c 20mg\n"
        "📍 <b>Адрес:</b> гр. Пловдив, ул. Главна 1 (Коригиран тел: +359888999888)\n"
        "━━━━━━━━━━━━━━━\n"
        f"<b>Total: {money(1250)}</b>\n\n"
        "<i>Want to change something? Just write to us.</i>"
    )
    markup = kb(
        [("✅ I agree", "demo_step7")],
        [("💬 Задай въпрос", "demo_ask")],
    )
    await cb.message.answer(caption, reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data == "demo_ask")
async def on_ask(cb: CallbackQuery) -> None:
    await cb.answer("💬 В реалната платформа тук се отваря директен чат в темата.", show_alert=True)

# СТЪПКА 7
@router.callback_query(F.data == "demo_step7")
async def step7_payment(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 7: Плащане и комисионна")
    await live_animation(cb.message.bot, cb.message.chat.id, "Регистриране на плащането")
    
    fee = round(1250 * COMMISSION_PCT / 100, 2)
    
    await cb.message.answer(
        "💳 <b>[Етап 7 от 10] Линк за плащане и отразяване</b>\n\n"
        "• Вендорът изпраща сигурен линк за плащане.\n"
        "• Клиентът плаща и потвърждава в чата: <i>„Готово, платих го!“</i>\n"
        "• Вендорът натиска системния бутон <b>✅ Paid</b> в служебната тема.\n\n"
        f"<blockquote>💰 <i>Финансов отчет:</i> Платформата автоматично отчита платформена комисионна (за демото е заложена примерна стойност от <b>{COMMISSION_PCT}%</b> или <b>${fee} USD</b>) към твоя панел.</blockquote>",
        reply_markup=kb([("👉 Виж динамиката на иконките в групата", "demo_step8")]),
        parse_mode="HTML"
    )

# СТЪПКА 8
@router.callback_query(F.data == "demo_step8")
async def step8_icons(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 8: Визуален контрол с иконки")
    await pause(cb.message.bot, cb.message.chat.id, 0.8)
    
    await cb.message.answer(
        "🏷️ <b>[Етап 8 от 10] Динамични статуси на темите в Telegram</b>\n\n"
        "Заглавието на темата в групата се променя автоматично на живо:\n\n"
        "• 🆕 <code>#1042 · Client Name</code> – Нов клиент (входящ лид).\n"
        "• 📦 <code>#1042 · Client Name</code> – Изпратена оферта.\n"
        "• 🔒 <code>#1042 · Client Name</code> – Приета оферта от клиента.\n"
        "• 🟢 <code>#1042 · Client Name</code> – Успешно платено и затворено!\n\n"
        "<i>Пълен контрол с един поглед върху списъка с теми.</i>",
        reply_markup=kb([("👉 Виж как работи командата /commission на живо", "demo_step9")]),
        parse_mode="HTML"
    )

# СТЪПКА 9: Симулация на реалния панел за комисионни /commission
@router.callback_query(F.data == "demo_step9")
async def step9_commission_panel(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 9: Комисионен панел /commission")
    await live_animation(cb.message.bot, cb.message.chat.id, "Извличане на отчетите от базата данни")
    
    await cb.message.answer(
        "📊 <b>[Етап 9 от 10] Реалният изглед на командата /commission</b>\n\n"
        "Когато администраторът или вендорът напише <code>/commission</code> в системата, софтуерът генерира следния точен отчет в реално време:\n\n"
        "----------------------------------------\n"
        "📊 <b>COMMISSION & SALES STATS (NOVAGENIX)</b>\n\n"
        "📦 Total Locked Offers: 1\n"
        "💰 Total Sales Volume: $1,250.00 USD\n"
        "💎 Total Commission (10%): $125.00 USD\n"
        "✅ Already Paid: $0.00 USD\n"
        "⏳ <b>Remaining Due (Unpaid):</b> $125.00 USD\n\n"
        "━━━━━━━━━━━━\n"
        "📌 <b>UNPAID DEALS BREAKDOWN:</b>\n"
        "🏷️ <b>Offer:</b> ORD-1042 | 🏢 <b>Vendor:</b> Novagenix Peptides\n"
        "👤 <b>Buyer:</b> Григор Петров\n"
        "💰 <b>Total:</b> $1,250.00 USD | 💎 <b>Commission:</b> <b>$125.00 USD</b>\n"
        "----------------------------------------\n\n"
        "<i>Администраторът разполага с активен системен бутон 🟢 <b>Mark Paid (ORD-1042)</b> за моментално уреждане на сметката с едно докосване!</i>",
        reply_markup=kb([("👉 Към финала на симулацията", "demo_step10")]),
        parse_mode="HTML"
    )

# СТЪПКА 10
@router.callback_query(F.data == "demo_step10")
async def step10_complete(cb: CallbackQuery) -> None:
    await cb.answer()
    await mark(cb, "Стъпка 10: Финал")
    await pause(cb.message.bot, cb.message.chat.id, 0.8)
    
    await cb.message.answer(
        "🎉 <b>[Етап 10 от 10] Тракинг, доставка и успешен финал</b>\n\n"
        "• Вендорът изпраща тракинг номер: <code>BG987654321</code>\n"
        "• Клиентът получава пратката и пише: <b>„Пратката пристигна, всичко е перфектно, много ви благодаря!“</b>\n\n"
        "🪄 <b>Голямата картина:</b> Пълна автоматизация, нулеви пропуснати детайли, прозрачни комисионни и доволни клиенти!",
        reply_markup=kb(
            [("💬 Свържи се за интеграция на платформата", CONTACT_URL)],
            [("🔁 Пусни симулацията отново", "demo_restart")],
        ),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "demo_restart")
async def on_restart(cb: CallbackQuery) -> None:
    await cb.answer()
    await run_intro(cb.message.bot, cb.message.chat.id)
