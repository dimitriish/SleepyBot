import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

load_dotenv()
logger = logging.getLogger(__name__)


def rag_prompt(prompt):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "You are helpful sleep assistant. You will be given retrieved data from our database."
                        "Answer question from user message based on retrieved documents if possible. "
                        "Otherwise answer something from your knowledge"
             },
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def fill_today(prompt):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    logger.info(f"Request to LLM: {prompt}")
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sophisticated sleep assistant. You should use extract slots of states from text."
                    "Output format as json:{"
                    "\"mood\": None,"
                    "\"good_things\": None,"
                    "\"bad_things\": None,"
                    "\"tomorrow_plans\": None"
                    "}"
                    "fill Nones by information from message. If there slot is not stated write null"
                    "In answer must be only json like output format"
                )
            },
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        temperature=0
    )
    logger.info(f"Response from LLM {response.choices[0].message.content.lower().strip()}")
    response_json = json.loads(response.choices[0].message.content.lower().strip())
    return response_json


def left_for_today(prompt):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    logger.info(f"Request to LLM: {prompt}")
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sophisticated sleep assistant. You need to ask user to fill Nones from dict."
                    "Don't say hello, the dialog has already started. Here's a dict:"
                )
            },
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        temperature=0.3
    )
    logger.info(f"Response from LLM {response.choices[0].message.content.lower().strip()}")
    return response.choices[0].message.content.strip()


def get_intent(ctx, intent):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    logger.info(f"Request to LLM: message: {ctx.last_user_message()}\nintent: {intent}")
    response = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "You are helpful sleep assistant."
                        "Based on message history you must decide whether such an intent exists (Does user want it or not)."
                        "Write only \"yes\" or \"no\""
                        "examples: message: What can you do?\n intent: know more about bot"
                        "\nresponse: yes"},
            {"role": "assistant", "content": ctx.last_bot_message()},
            {"role": "user", "content": f"message: {ctx.last_user_message()}\n intent: {intent}"},
        ],
        model="gpt-3.5-turbo",
        temperature=0
    )
    logger.info(f"Response from LLM {response.choices[0].message.content.lower().strip()}")
    return response.choices[0].message.content.strip()
