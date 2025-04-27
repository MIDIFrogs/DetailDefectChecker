import telebot
import io
import os
import yaml
import numpy as np
import response
import requests

# Resources
config = {}
if (os.path.exists("startup.config")):
    with open("startup.config") as configFile:
        keys = configFile.readlines()
        for line in keys:
            key, value = map(lambda x: x.strip(), line.split("="))
            config[key] = value


def call_api(image: bytes, scale_x: float = 0.01, scale_y: float = 0.01) -> response.Response:
    url = "http://localhost:5000/api/process"  
    files = {'image': ('image.png', image)}  # Указываем имя файла и его содержимое
    data = {
        'scale_x': scale_x,
        'scale_y': scale_y
    }
    response_data = requests.post(url, files=files, data=data)  # Отправляем файл как часть формы
        
    if response_data.status_code == 200:
        return response.from_json(response_data.text)  # Десериализуем JSON в объект Response
    else:
        print(f"Error: {response_data.status_code}, {response_data.text}")
        return {}

def download_image(image_id: int) -> bytes:
    url = f"http://localhost:5000/api/download/{image_id}"  
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.content  
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


# Bot helper functions
def createAnswer(response, id):    
    for detection in response.detections:
        answer = f"Деталь: {detection.class_name}\n"
        if detection.passed:
            answer += "Деталь идеальна: ✅\n"
        else:
            answer += "Деталь не прошла проверку: ❌\n"
            answer += f"Шероховатость: {'✅' if not detection.is_rough else '❌'}\n"
            answer += f"Соответствие размеру: {'✅' if detection.size_passed else '❌'}\n"
            answer += f"Количество дефектов: {detection.defects_count}\n"
        bot.send_message(id, answer)
    bot.send_photo(id, download_image(response.download_id))

# Bot section

TOKEN = config.get("Token", os.environ.get("Token"))
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    '''Answers on bot '/start' command
    '''
    sticker = open('Resources/hi.webp', 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, "Здравствуй, дорогой пользователь. Наш бот поможет тебе с обработкой дефектов деталей . Просто отправь фото и бот ответит, есть ли на нем дефекты, при наличии подсветит их Также определит размер детали и определит есть ли на ней шероховатость.")

@bot.message_handler(content_types=['photo'])
def OnPhotoRecieve(message):
    '''Handles photo request from user.'''
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        # Получаем байтовые данные изображения
        image_data = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        response_obj = call_api(image_data)  # Передаем байтовые данные в API
        if isinstance(response_obj, response.Response):  # Проверяем, что это объект Response
            createAnswer(response_obj, message.chat.id)
        else:
            bot.send_message(message.chat.id, "Ошибка при обработке ответа от сервера.")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла непредвиденная ошибка. Пожалуйста, попробуйте снова или используйте другое изображение.")
        print(e)

@bot.message_handler(content_types=['text', 'sticker', 'video' 'voice'])
def OnWrongContentType(message):
    '''Handles any wrong data types receiving.

    Args:
        'message': Telegram message with any content instead of photos.
    '''
    sticker = open('Resources/wrong.webp', 'rb')
    bot.send_message(message.chat.id, "К сожалению, это не то, что мне нужно. Я могу обрабатывать только фотографии форматов: jpg,jpeg,png, а не какой-то случайный текст. Чтобы продолжить работу мне нужно получить конкретное изображение.")
    bot.send_sticker(message.chat.id, sticker)

@bot.message_handler(content_types=['document'])
def OnFileRecieve(message):
    '''Handles any wrong data types receiving.

    Args:
        'message': Telegram message with any content instead of photos.
    '''
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = call_api(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))
        createAnswer(response, message.chat.id)
    except:

        bot.send_message(message.chat.id, "Произошла непредвиденная ошибка. Пожалуйста, попробуйте снова или используйте другое изображение.")
# Startup the bot
bot.polling(none_stop = True)
