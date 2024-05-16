import os
from bot.pipeline import pipeline
from bot.config import logger, load_environment
from bot.context import Context
import time
from datetime import datetime, date
from rag.faiss_index import FaissRag

load_environment()

# Initialize your Telegram bot token
faiss_idx = FaissRag()
ctx = Context(pipeline['technical_flow'].nodes["start_node"], faiss_idx)

def base_message_step():
    response = ctx.current_node(ctx)
    if response is not None:
        print(f'bot: {response}')
        ctx.add_response(response)
    logger.info(f"Current node: {ctx.current_node.name}")


def handle_message(message):
    print(f'user: {message}')
    ctx.user_message_history.append(message)
    ctx.current_node.transition(ctx, pipeline)
    base_message_step()


happy_path = {
    '/start': pipeline['unsubscribed_flow'].nodes['greetings_node'],
    'I want to know more about you': pipeline['unsubscribed_flow'].nodes['more_info_node'],
    'I want to buy sub': pipeline['unsubscribed_flow'].nodes['buying_sub_node'],
    '0000': pipeline['unsubscribed_flow'].nodes['buying_sub_node'],
    '1234': pipeline['subscribed_flow'].nodes['greetings_node_after_sub']
}
ctx.current_node = pipeline['technical_flow'].nodes["start_node"]
for msg in happy_path:
    handle_message(msg)
    assert ctx.current_node == happy_path[msg]


daily_ritual_path = {
    'Good': pipeline['subscribed_flow'].nodes['daily_rituals_node'],
    'Good: done project, Bad: no sleep': pipeline['subscribed_flow'].nodes['daily_rituals_node'],
    'Plans: Chill all day': pipeline['subscribed_flow'].nodes['rag_node'],

}
tomorrow_plans_none = [False, False, True]
ctx.current_node = pipeline['subscribed_flow'].nodes["subscribed_flow"]
for i, msg in enumerate(daily_ritual_path):
    handle_message(msg)
    assert ctx.current_node == happy_path[msg]
    assert (ctx.daily_statuses[str(date.today())]['tomorrow_plans'] is None) == tomorrow_plans_none[i]
