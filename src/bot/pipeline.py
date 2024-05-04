import json
from bot.config import logger
from bot.dialog_flow import DialogFlow, DialogNode
from bot.llm_api import get_intent, rag_prompt, fill_today, left_for_today
from datetime import date


def greetings_node_after_sub_response(context):
    context.is_subscribed = True
    return "Thank you for subscribing! Now that you're a premium member, you can ask me anything. "\
           "From daily reminders to real-time weather updates, I'm here to assist. What can I help you with today?"


def daily_ritual_node_response(context):
    today = date.today()
    if str(today) not in context.daily_statuses:
        context.daily_statuses[f'{today}'] = {
            "mood": None,
            "good_things": None,
            "bad_things": None,
            "tomorrow_plans": None
        }
        return "Let's make daily rituals! Tell me how are you today?"
    prompt = f"assistant: {context.last_bot_message()}\n user: {context.last_user_message()}\ncurrent_state: {context.daily_statuses[f'{today}']}"
    updated_daily = fill_today(prompt)
    for s in context.daily_statuses[f'{today}']:
        if context.daily_statuses[f'{today}'][s] is None:
            context.daily_statuses[f'{today}'][s] = updated_daily[s]
    if None not in context.daily_statuses[f'{today}'].values():
        logger.info(f"statuses for today: {context.daily_statuses[f'{today}']}")
        return "Thanks a lot for your answers. Tomorrow will be a good day. Sleep well!"
    return left_for_today(str(context.daily_statuses[f'{today}']))


def rag_node_response(context):
    query = context.last_user_message()
    retrieved = context.faiss_idx.retrieve_documents(query)
    prompt = f"last_user_message: {context.last_user_message()}\nretrieved documents: {'\n'.join(retrieved)}"
    response = rag_prompt(prompt) + "\nI would glad to answer your questions."
    return response


pipeline = {
    "technical_flow": DialogFlow(
        {
            "start_node": DialogNode(
                "start_node",
                [
                    (lambda context: context.last_user_message() == "/start", "unsubscribed_flow", "greetings_node"),
                    (lambda context: True, "technical_flow", "start_node")
                ]
            ),
        }
    ),
    "unsubscribed_flow": DialogFlow(
        {
            "greetings_node": DialogNode(
                "greetings_node",
                [
                    (lambda context: get_intent(context, "know more about chatbot") == "yes", "unsubscribed_flow",
                     "more_info_node"),
                    (lambda context: get_intent(context, "buy subscription/subscribe") == "yes", "unsubscribed_flow",
                     "buying_sub_node"),
                    (lambda context: True, "unsubscribed_flow", "fallback_node")
                ],
                lambda
                    context: "Hi! I'm SleepyBot, your personal assistant. Whether you need help with daily tasks or just want to chat, I'm here! "
                             "If you're interested in more features, you can learn more or subscribe for additional services. Just tell me what you'd like to do next!"
            ),
            "more_info_node": DialogNode(
                "more_info_node",
                [
                    (lambda context: get_intent(context, "buy subscription/subscribe") == "yes", "unsubscribed_flow",
                     "buying_sub_node"),
                    (lambda context: True, "unsubscribed_flow", "fallback_node")
                ],
                lambda
                    context: "I can assist with scheduling, reminders, entertainment, and even provide updates on news and weather. "
                             "For unlimited access to all features, you can subscribe for only $1 per month! Interested in subscribing?"
            ),
            "buying_sub_node": DialogNode(
                "buying_sub_node",
                [
                    (lambda context: context.last_user_message() == "1234", "subscribed_flow",
                     "greetings_node_after_sub"),
                    (lambda context: get_intent(context, "know more about chatbot") == "yes", "unsubscribed_flow",
                     "more_info_node"),
                    (lambda context: context.last_user_message().isdigit(), "unsubscribed_flow", "buying_sub_node"),
                    (lambda context: True, "unsubscribed_flow", "fallback_node")
                ],
                lambda
                    context: "To subscribe, simply click on this https://example.com/subscribe and follow the instructions. "
                             "Once you have subscribed, send me the code you received. I'm excited to offer you even more personalized services!"
            ),
            "remember_me": DialogNode(
                "remember_me",
                [
                    (lambda context: get_intent(context, "know more about chatbot") == "yes", "unsubscribed_flow",
                     "more_info_node"),
                    (lambda context: get_intent(context, "buy subscription/subscribe") == "yes", "unsubscribed_flow",
                     "buying_sub_node"),
                    (lambda context: True, "unsubscribed_flow", "fallback_node")
                ],
                lambda
                    context: "It looks like we haven't talked in a while. I'm still here to help you whenever you need! "
                             "Would you like to know more about what I can do or perhaps consider subscribing to unlock full features?"
            ),
            "fallback_node": DialogNode(
                "fallback_node",
                [
                    (lambda context: get_intent(context, "know more about chatbot") == "yes", "unsubscribed_flow",
                     "more_info_node"),
                    (lambda context: get_intent(context, "buy subscription/subscribe") == "yes", "unsubscribed_flow",
                     "buying_sub_node"),
                    (lambda context: True, "unsubscribed_flow", "fallback_node")
                ],
                lambda
                    context: "I'm not sure I understood that. Could you please repeat, or if you need help, just type 'help'! "
                             "To access all my features without limitations, consider subscribing. Just say 'subscribe' to learn how!"
            ),
        }
    ),
    "subscribed_flow": DialogFlow(
        {
            "greetings_node_after_sub": DialogNode(
                "greetings_node_after_sub",
                [
                    (lambda context: True, "subscribed_flow", "rag_node")
                ],
                greetings_node_after_sub_response
            ),
            "rag_node": DialogNode(
                "rag_node",
                [
                    (lambda context: True, "subscribed_flow", "rag_node")
                ],
                rag_node_response
            ),
            "daily_rituals_node": DialogNode(
                "daily_rituals_node",
                [
                    (lambda context: None not in context.daily_statuses[f'{date.today()}'].values(), "subscribed_flow",
                     "rag_node"),
                    (lambda context: True, "subscribed_flow", "daily_rituals_node")
                ],
                daily_ritual_node_response
            ),
        }
    ),
}
