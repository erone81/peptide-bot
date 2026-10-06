ADMIN_IDS = [8912162282]
ADMIN_USERNAMES = ["g3orgel", "georgel"]

def is_admin(user: types.User) -> bool:
    if not user:
        return False
    if user.id in ADMIN_IDS:
        return True
    if user.username and user.username.lower() in ADMIN_USERNAMES:
        return True
    return False

# Публикуване на главния въвеждащ текст за директорията
@dp.message(Command("post_directory_info"))
async def post_directory_info_handler(message: types.Message):
    if not is_admin(message.from_user):
        return
    
    text = (
        "🛡️ <b>VERIFIED VENDORS DIRECTORY</b>\n\n"
        "Here you will find rigorously vetted and continuously monitored peptide manufacturers. Every supplier listed meets our strict standards for quality, reliability, and secure fulfillment.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 <b>HOW TO GET STARTED:</b>\n\n"
        "<b>1️⃣ Select a Vendor</b>\n"
        "Browse our verified partners below and review their capabilities and terms.\n\n"
        "<b>2️⃣ Open Direct Chat</b>\n"
        "Tap the button beneath each vendor profile to launch an official, secure session.\n\n"
        "<b>3️⃣ Review Catalog &amp; Policies</b>\n"
        "Receive the complete batch price list, warehouse stock, and delivery guidelines automatically.\n\n"
        "<b>4️⃣ Inquire &amp; Order</b>\n"
        "Discuss orders, confirm custom quantities, and complete transactions directly with the vendor team.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
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

# Публикуване на визитката на вендор
@dp.message(Command("post_vendor"))
async def post_vendor_card(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user):
        print(f"Unauthorized post_vendor attempt by user ID {message.from_user.id} (@{message.from_user.username})")
        return
    
    vendor_key = (command.args or "tidetron").strip().lower()
    v = VENDORS.get(vendor_key)
    if not v:
        await message.reply(f"Vendor '{vendor_key}' not found. Available: {', '.join(VENDORS.keys())}")
        return

    banner_file = v["banner_path"]
    thread_id = message.message_thread_id

    try:
        if os.path.exists(banner_file):
            await bot.send_photo(
                message.chat.id,
                FSInputFile(banner_file),
                caption=v["post_caption"],
                reply_markup=public_vendor_keyboard(vendor_key),
                parse_mode="HTML",
                message_thread_id=thread_id
            )
        else:
            await bot.send_message(
                message.chat.id,
                v["post_caption"],
                reply_markup=public_vendor_keyboard(vendor_key),
                parse_mode="HTML",
                message_thread_id=thread_id
            )
    except Exception as e:
        print("Error posting vendor card:", e)
        await message.reply(f"Error posting card: {e}")

    try:
        await message.delete()
    except Exception:
        pass
