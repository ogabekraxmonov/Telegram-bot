import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8174672894:AAFF4PJJaPRhE3tMXBmfOhIaQ6uWiI8yUHU'
ADMIN_ID = 536572122

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchi menyu tanlaganini saqlaymiz
user_menu_selected = {}  # {user_id: True/False}
# Adminning reply qilgan xabarida foydalanuvchi ID sini topish uchun
# forward_to_admin da xabar yuborilganda: message_id -> user_id
pending_replies = {}  # {admin_message_id: user_id}

# --- KLAVIATURA ---
menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_premium = KeyboardButton("Premium🌟")
btn_stars = KeyboardButton("Buy Telegram Stars")
menu.add(btn_premium, btn_stars)

# --- START ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_menu_selected[message.from_user.id] = False
    text = (
        "Assalomu alaykum, botimizga xush kelibsiz!\n"
        "Menyulardan birini tanlang!"
    )
    await message.answer(text, reply_markup=menu)

# --- PREMIUM MENYUSI ---
@dp.message_handler(lambda message: message.text == "Premium🌟")
async def show_premium(message: types.Message):
    user_menu_selected[message.from_user.id] = True
    text = (
        "✨ Akkauntga kirib ⚡️\n"
        "⭐ 1 oylik  ---  40 ming so'm\n"
        "⭐ 1 yillik ---  275 ming so'm\n\n"
        "Akkauntga kirmasdan 🎁\n"
        "🎁 3 oylik  ---  165 ming so'm\n"
        "🎁 6 oylik  ---  225 ming so'm\n"
        "🎁 1 yillik ---  395 ming so'm\n\n"
        "Buyurtma qilish uchun:\n"
        "💳 `9860082455120491` shu kartaga summa o'tkazing "
        "va chekni rasmga olib shu yerga yuboring!"
    )
    await message.answer(text, parse_mode="Markdown")

# --- STARS MENYUSI ---
@dp.message_handler(lambda message: message.text == "Buy Telegram Stars")
async def show_stars(message: types.Message):
    user_menu_selected[message.from_user.id] = True
    text = (
        "⭐ *Telegram Stars* ⭐\n\n"
        "✨ 100 Stars - 30.000 uzs\n"
        "✨ 250 Stars - 65.000 uzs\n"
        "✨ 500 Stars - 125.000 uzs\n"
        "✨ 1000 Stars - 245.000 uzs\n\n"
        "To'lov uchun karta:\n"
        "💳 `9860082455120491`\n"
        "To'lovni amalga oshirib, chekni yuboring."
    )
    await message.answer(text, parse_mode="Markdown")

# --- ADMIN REPLY QILGANDA FOYDALANUVCHIGA YUBORISH ---
@dp.message_handler(
    lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None,
    content_types=['text', 'photo', 'document']
)
async def admin_reply_to_user(message: types.Message):
    replied_msg_id = message.reply_to_message.message_id
    user_id = pending_replies.get(replied_msg_id)

    if not user_id:
        await message.answer("⚠️ Bu xabarga reply qilib foydalanuvchiga yozib bo'lmaydi.")
        return

    try:
        if message.text:
            await bot.send_message(user_id, message.text)
        elif message.photo:
            await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
        elif message.document:
            await bot.send_document(user_id, message.document.file_id, caption=message.caption or "")
        await message.answer("✅ Javob foydalanuvchiga yuborildi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# --- FOYDALANUVCHIDAN ADMINГА XABAR YUBORISH ---
@dp.message_handler(content_types=['photo', 'document', 'text'])
async def forward_to_admin(message: types.Message):
    user_id = message.from_user.id

    # Agar menyu tanlanmagan bo'lsa
    if not user_menu_selected.get(user_id, False):
        await message.answer("❗ Iltimos, avval menyulardan birini tanlang!")
        return

    # Foydalanuvchi ma'lumoti
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    user_info = (
        f"📩 Yangi buyurtma!\n"
        f"👤 Ism: {message.from_user.full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {user_id}"
    )

    # Avval info xabar yuboramiz
    await bot.send_message(ADMIN_ID, user_info)

    # Keyin xabarni forward qilamiz va message_id sini saqlaymiz
    forwarded = await message.forward(ADMIN_ID)
    pending_replies[forwarded.message_id] = user_id

    await message.answer("✅ Sizning so'rovingiz adminga yuborildi. Tez orada javob beramiz!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    
