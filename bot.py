from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
import uuid

# قاعدة بيانات مؤقتة على شكل قاموس
users = {}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("أوافق ✅", callback_data="agree")],
        [InlineKeyboardButton("لا أوافق ❌", callback_data="no")]
    ]
    await update.message.reply_text(
        "مرحباً 👋\n"
        "قبل الدخول في المسابقة، نحتاج بعض البيانات (الاسم، البريد الإلكتروني، رقم الهاتف، رقم المسابقة)\n"
        "وسيتم استخدامها فقط لأغراض تنظيم المسابقة والتواصل معك.\n\nهل توافق؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# أزرار الموافقة / رفض
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "agree":
        context.user_data["step"] = "name"
        await query.message.reply_text("اكتب اسمك الكامل:")
    else:
        await query.message.reply_text("لا يمكن المشاركة بدون موافقة 🙏")

# التعامل مع الرسائل النصية لكل خطوة
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
        await update.message.reply_text("أدخل رقم المسابقة / رقم الهوية:")

    elif step == "id":
        card_id = str(uuid.uuid4())[:8]  # رقم بطاقة فريد
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

# سحب توكن البوت من متغير البيئة
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# إضافة الهاندلرز
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))

# تشغيل البوت
app.run_polling()
