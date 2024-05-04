# SleepyBot - Your Personal Telegram Assistant
SleepyBot is a sophisticated Telegram bot designed to assist users with daily tasks, provide information, and offer a subscription-based service for enhanced features. Built with Python and leveraging the asyncio library for efficient asynchronous operations, SleepyBot aims to deliver a responsive and personalized user experience.

## Features
 - User Interaction: Engage in simple conversations, provide information, and respond to user queries.
 - Subscription Service: Users can subscribe to unlock premium features, including advanced task management and personalized notifications.
 - Dynamic Responses: Context-aware dialogue management allowing for natural and meaningful interactions.
 - Scheduled Tasks: Perform actions at scheduled times, such as daily reminders or updates.
 - Remembrance Feature: Gently prompts users if they have not interacted with the bot for a specified period.

## Installation
### 1. Clone the repository:
```commandline
git clone https://github.com/dimitriish/sleepybot.git
cd sleepybot
```
### 2. Install dependencies:
```commandline
pip install -r requirements.txt
```
### 3. Set up environment variables:
Add your TG_BOT_TOKEN and OPENAI_API_KEY
```commandline
OPENAI_API_KEY=
TG_BOT_TOKEN=
```
### 4. Run the bot:
```commandline
python src/app.py
```

## Components
Two main flows: unsubscribed and subscribed

For unsubscribed flow: 
 - greeting_node 
 - more_info_node
 - buy_sub_node
 - 