import telebot

# Import your answer_question function here
from gpt_script import answer_question
from info import *
import os

# Create a new Telebot instance
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))


# Define a handler for the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, start_info)
@bot.message_handler(commands=['fill_formulary'])
def handle_formulary(message):
    bot.reply_to(message, fill_formulary)
# Define a handler for incoming messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Get the user's message
    user_message = message.text

    # Generate a response using answer_question function
    response = answer_question(user_message)

    # Send the response back to the user
    bot.reply_to(message, response)

# Start the bot
bot.polling()
