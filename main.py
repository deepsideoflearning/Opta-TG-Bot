import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

due = 0
step = -1
list = ["Self belief and hard work will always lead to success!",
        "If opportunity doesn't knock, build a door!",
        "Without mathematics, there is nothing you can do.",
        "I'd rather die of exhaustion than of boredom!",
        "Sleep is over rated!",
        "We cannot solve our problems with the same thinking we used to create them, the most valuable skill is the ability to unlearn things and quickly learn new ways of thinking."]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update.effective_chat.id)+' '+update.message.text)

async def core(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args_combined = ' '.join(context.args)
    await context.bot.send_message(chat_id=-1002131476848, text=args_combined)

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args_combined = ' '.join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=args_combined)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    global step, list
    
    job = context.job
    step = step + 1 if step<len(list)-1 else 0
    message = 'Motivational quote of the hour (next one in '+str(int(due))+' minutes): \n\n----------\n'+list[step]+'\n----------'

    await context.bot.send_message(job.chat_id, text=message)
    set_timer_again(context)
        #f"Beep! {job.data} seconds are over!")

def set_timer_again(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    global due
    
    #chat_id = update.effective_message.chat_id

    # args[0] should contain the time for the timer in seconds
    job = context.job
    chat_id = job.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(alarm, due*60, chat_id=chat_id, name=str(chat_id), data=due)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    global due
    
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, 5, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


if __name__ == '__main__':
    application = ApplicationBuilder().token('6764242110:AAGgJVJILI0q7cZRGg5Cda7UfrWx7yk8cd0').build()
    
    start_handler = CommandHandler(['start','help'], start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    core_handler = CommandHandler('core', core)
    test_handler = CommandHandler('test', test)
    set_handler = CommandHandler("set", set_timer)
    unset_handler = CommandHandler("unset", unset)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    #application.add_handler(echo_handler)
    application.add_handler(core_handler)
    application.add_handler(test_handler)
    application.add_handler(set_handler)
    application.add_handler(unset_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
