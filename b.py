from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio
import time

user_timers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "User"
    await update.message.reply_text(f"👋 Hello {name}! \nHow many minutes would you like to set the timer for? ⏰ (Please enter a number)")
    return

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Please enter only numbers, like: 2, 5, 10, etc.")
        return
    minutes = int(update.message.text)
    chat_id = update.effective_chat.id
    user_timers[chat_id] = {"stop_spam": False}
    await update.message.reply_text(f"✅ Timer started for {minutes} minute(s)! ⏳")
    await asyncio.create_task(timer_flow(update, context, chat_id, minutes))

async def timer_flow(update, context, chat_id, minutes):
    await asyncio.sleep(minutes * 60)
    keyboard = [[InlineKeyboardButton("🛑 Stop Timer", callback_data='stop_timer')]]
    await context.bot.send_message(
        chat_id,
        "⏰ Your timer is up! Time to get back to work! 🚀\nPress 'Stop Timer' to prevent spam from starting! ⏹️",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Wait up to 60 seconds for the stop timer button
    timer_stop = False
    for i in range(60):
        if user_timers[chat_id].get("timer_stopped"):
            timer_stop = True
            break
        await asyncio.sleep(1)

    # If not stopped, start spam messages
    if not timer_stop:
        await asyncio.create_task(spam_flow(context, chat_id))

async def stop_timer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_timers[chat_id]["timer_stopped"] = True
    await query.answer("⏹️ Timer stopped!")
    await query.edit_message_text("✅ Timer stopped.")

async def spam_flow(context, chat_id):
    spam_duration = 60  # 1 minute of spam
    start_time = time.time()
    count = 0
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⛔ Stop Spam", callback_data='stop_spam')]])

    while not user_timers[chat_id]['stop_spam'] and (time.time() - start_time) < spam_duration:
        countdown = spam_duration - int(time.time() - start_time)
        msg_text = f"⚡ YOUR TIMER IS UP! GET BACK TO WORK! ⚡\n⏳ Spam time left: {countdown}s"
        if count == 0:
            await context.bot.send_message(chat_id, msg_text, reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id, msg_text)
        await asyncio.sleep(0.6)  # Sends about 100 spam messages in 1 minute
        count += 1
        # Spam will only stop when stop_spam is set

async def stop_spam_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_timers[chat_id]['stop_spam'] = True
    await query.answer("🚫 Spam stopped!")
    await query.edit_message_text("✅ Spam stopped.")

def main():
    app = Application.builder().token("8473327495:AAHA_WSzeeNB-U19tqwGFVvLHbJk1YFUcYA").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask_time))
    app.add_handler(CallbackQueryHandler(stop_timer_callback, pattern='stop_timer'))
    app.add_handler(CallbackQueryHandler(stop_spam_callback, pattern='stop_spam'))
    print("🤖 Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()
