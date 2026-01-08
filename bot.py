from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *
import uuid

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("أوافق ✅", callback_data="agree")],
        [InlineKeyboardButton("لا أوافق ❌", callback_data="no")]
    ]
    await update.message.reply_text(
        "مرحباً 👋\nقبل الدخول في المسابقة، نحتاج بعض البيانات (الاسم، البريد الإلكتروني، رقم الهاتف، رقم الهوية)\n"
        "وسيتم استخدامها فقط لأغراض تنظيم المسابقة والتواصل معك.\n\nهل توافق؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "agree":
        context.user_data["step"] = "name"
        await q.message.reply_text("اكتب اسمك الكامل:")
    else:
        await q.message.reply_text("لا يمكن المشاركة بدون موافقة 🙏")

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text
    step = context.user_data.get("step")

    if step == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "email"
        await update.message.reply_text("أدخل بريدك الإلكتروني:")

    elif step == "email":
        context.user_data["email"] = text
        context.user_data["step"] = "phone"
        await update.message.reply_text("أدخل رقم هاتفك:")

    elif step == "phone":
        context.user_data["phone"] = text
        context.user_data["step"] = "id"
        await update.message.reply_text("أدخل رقم الهوية / رقم المسابقة:")

    elif step == "id":
        card_id = str(uuid.uuid4())[:8]

        users[uid] = {
            "name": context.user_data["name"],
            "email": context.user_data["email"],
            "phone": context.user_data["phone"],
            "id_number": text,
            "card": card_id
        }

        await update.message.reply_text(
            f"🎉 تم تسجيلك بنجاح!\n\n"
            f"🪪 بطاقة المشاركة الخاصة بك:\n"
            f"الاسم: {users[uid]['name']}\n"
            f"رقم البطاقة: {card_id}\n\n"
            f"احتفظ بها جيداً 💾"
        )

        context.user_data.clear()

app = ApplicationBuilder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))

app.run_polling()
