import telebot
import io
import os
import yaml
import numpy as np
import response

# YOLO
model  = YOLO('model.pt')

# Resources
config = {}
if (os.path.exists("startup.config")):
    with open("startup.config") as configFile:
        keys = configFile.readlines()
        for line in keys:
            key, value = map(lambda x: x.strip(), line.split("="))
            config[key] = value


# Bot helper functions
def createAnswer(response: Response):
    answer = ""
    
    for detection in response.detections:
        if detection.passed:
            answer += "Деталь идеальна: ✅\n"
        else:
            answer += "Деталь не прошла проверку: ❌\n"
            answer += f"Шероховатость: {'✅' if detection.is_rough else '❌'}\n"
            answer += f"Соответствие размеру: {'✅' if detection.size_passed else '❌'}\n"
            answer += f"Количество дефектов: {detection.defects_count}\n"
    return answer

# Bot section

TOKEN = config.get("Token", os.environ.get("Token"))
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    '''Answers on bot '/start' command
    '''
    sticker = open('Resources/hi.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, localization["HelloMessage"])

@bot.message_handler(content_types=['photo'])
def OnPhotoRecieve(message):
    '''Handles photo request from user.

    Args:
        'message': Telegram message with image for the bot. 
    '''
    try:
        bot.send_chat_action(message.chat.id, 'typing')\
        # Get the photo from user.
        photo = message.photo[-1]
        #Ivan take photo
        createAnswer(ivan.isCorrespondent(), ivan.isRough(), ivan.isDefective())
        bot.send_photo(message.chat.id, ivan.givePhoto()) 
    except:
        bot.send_message(message.chat.id, localization["UnexpectedErrorMessage"])

@bot.message_handler(content_types=['text', 'sticker', 'video' 'voice'])
def OnWrongContentType(message):
    '''Handles any wrong data types receiving.

    Args:
        'message': Telegram message with any content instead of photos.
    '''
    sticker = open('Resources/wrong.webp', 'rb')
    bot.send_message(message.chat.id, localization["WrongTypeMessage"])
    bot.send_sticker(message.chat.id, sticker)

@bot.message_handler(content_types=['document'])
def OnFileRecieve(message):
    '''Handles any wrong data types receiving.

    Args:
        'message': Telegram message with any content instead of photos.
    '''
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file = message.document
        if file.file_name.endswith('.jpg') or file.file_name.endswith('.jpeg') or file.file_name.endswith('.png'):
            boxImage(message, file)
        else:
            bot.send_message(message.chat.id, localization["WrongTypeMessage"])
    except:
        bot.send_message(message.chat.id, localization["UnexpectedErrorMessage"])

# Startup the bot
bot.polling(none_stop = True)
