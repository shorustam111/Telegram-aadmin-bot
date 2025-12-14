import os
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
TOKEN = "8523195504:AAFXb9Q_1R-pdbk_K1DDlERvMw4Au8sI3a8" # Render ENV dan olinadi
ADMIN_ID = 5667085885 # <-- BU YERGA O'Z TELEGRAM ID INGIZNI YOZING

DB_NAME = "users.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        name TEXT,
        age INTEGER
    )
    """)
    conn.commit()
    conn.close()

# ================= USER =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Ismingizni yuboring 👇")
    context.user_data["step"] = "name"

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step == "name":
        context.user_data["name"] = update.message.text
        context.user_data["step"] = "age"
        await update.message.reply_text("Yoshingizni yuboring 👇")

    elif step == "age":
        if not update.message.text.isdigit():
            await update.message.reply_text("❗ Iltimos, faqat raqam kiriting")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (telegram_id, name, age) VALUES (?, ?, ?)",
            (
                update.effective_user.id,
                context.user_data["name"],
                int(update.message.text)
            )
        )
        conn.commit()
        conn.close()

        await update.message.reply_text("✅ Ma'lumotlar saqlandi")
        context.user_data.clear()

# ================= ADMIN =================
def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Siz admin emassiz")
        return

    await update.message.reply_text(
        "🔐 ADMIN PANEL\n\n"
        "/users - foydalanuvchilar ro‘yxati\n"
        "/clear - bazani tozalash"
    )

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, age FROM users")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("📭 Baza bo‘sh")
        return

    text = "📋 FOYDALANUVCHILAR:\n\n"
    for i, (name, age) in enumerate(rows, 1):
        text += f"{i}. {name} — {age} yosh\n"

    await update.message.reply_text(text)

async def clear_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()

    await update.message.reply_text("🗑 Baza tozalandi!")

# ================= RUN =================
def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("clear", clear_db))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
