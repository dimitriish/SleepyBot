import asyncio
import os
from telebot.async_telebot import AsyncTeleBot
from bot.pipeline import pipeline
from bot.config import logger, load_environment
from bot.context import Context
import time
from datetime import datetime

from rag.faiss_index import FaissRag

load_environment()

# Initialize your Telegram bot token
bot = AsyncTeleBot(os.environ["TG_BOT_TOKEN"])
faiss_idx = FaissRag()
ctx = Context(pipeline['technical_flow'].nodes["start_node"], faiss_idx)


async def base_message_step():
    response = ctx.current_node(ctx)
    if response is not None:
        await bot.send_message(ctx.get_chat_id(), response)
        ctx.add_response(response)
    logger.info(f"Current node: {ctx.current_node.name}")


async def change_node(target_node):
    logger.info(f"Transitioned to {target_node.name}")
    ctx.current_node = target_node
    await base_message_step()


async def schedule_checker():
    while True:
        now = datetime.now()
        if (ctx.is_subscribed and
                str(now.date()) not in ctx.daily_statuses and
                now.hour == 1 and 15 <= now.minute < 45):
            await change_node(pipeline['subscribed_flow'].nodes["daily_rituals_node"])
        await asyncio.sleep(5)


async def remember_me_checker():
    while not ctx.is_subscribed:
        last_time = ctx.last_message_datetime()
        if last_time is not None and time.time() - last_time > 60 * 60 * 24:
            await change_node(pipeline['unsubscribed_flow'].nodes["remember_me"])
        await asyncio.sleep(60)


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    ctx.user_message_history.append(message)
    await ctx.current_node.transition(ctx, pipeline)
    await base_message_step()


@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    ctx.user_message_history.append(message)
    await ctx.current_node.transition(ctx, pipeline)
    await base_message_step()


async def main():
    logger.info("Server started")
    await asyncio.gather(
        schedule_checker(),
        remember_me_checker(),
        bot.polling(none_stop=True, interval=0.1)
    )


# Run the main coroutine
asyncio.run(main())
