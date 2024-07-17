from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, Bot

from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from dotenv import load_dotenv
import openai
import os
import aiohttp
import json


# подгружаем переменные окружения
load_dotenv()

# передаем секретные данные в переменные
TOKEN = os.environ.get("TG_TOKEN")


# передаем секретный токен chatgpt
openai.api_key = os.environ.get("OPENAI_API_KEY")

#############################################################################
# inline_frame = [[InlineKeyboardButton("Начать чат:", callback_data="SCAT")],
#                 # [InlineKeyboardButton("Осталось запросов:", callback_data="status")],
#                 # [InlineKeyboardButton("История сообщений:", callback_data="history")],
#                 ]
# inline_keyboard = InlineKeyboardMarkup(inline_frame)
#############################################################################

async def scat(update:Update, _):
    await update.callback_query.message.reply_text('Я консультант службы поддержки компании MEGACOMPANY. Пожалуйста, напишите свой вопрос.')

# функция для асинхронного общения с сhatgpt
async def get_answer_async(text):
    payload = {"text":text}
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/api/get_answer_async', json=payload) as resp:
            return await resp.json()


# функция-обработчик команды /start 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # при первом запуске бота добавляем этого пользователя и историю сообщений в словарь 
    if update.message.from_user.id not in context.bot_data.keys():
        context.bot_data[update.message.from_user.id] = {"remaining_requests": 3, "user_query": [], "bot_answer": []}
    
    
    # возвращаем текстовое сообщение пользователю
    await update.message.reply_text('Я консультант службы поддержки компании MEGACOMPANY. Пожалуйста, напишите свой вопрос.')


# # функция-обработчик команды /data 
# async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):

#     # создаем json и сохраняем в него словарь context.bot_data
#     with open('data.json', 'w') as fp:
#         json.dump(context.bot_data, fp)
    
#     # возвращаем текстовое сообщение пользователю
#     await update.message.reply_text('Данные сгружены')


# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # выполнение запроса в chatgpt
    first_message = await update.message.reply_text('Ваш запрос обрабатывается, пожалуйста подождите...')
    question = f'Ответь на вопрос клиента - {update.message.text}'
        
    res = await get_answer_async(question)
    await context.bot.edit_message_text(text=res['message'], chat_id=update.message.chat_id, message_id=first_message.message_id)

# функция-обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # получаем callback query из update
    query = update.callback_query

    # всплывающее уведомление
    await query.answer(f'Вы нажали на кнопку: {query.data}')
    
    # редактируем сообщение после нажатия
    # await query.edit_message_text(text=f"Вы нажали на кнопку: {query.data}")
    ##############################################################################
    # функция обработки нажатий кнопок
    if query.data=='scat':
       await scat(update, context)
    # elif query.data=='status':
    #     await status(update, context)
    ###############################################################################


def main():

    # Создание приложения и передача в него токена бота
    application = Application.builder().token(TOKEN).build()
    
    # # Отправка сообщения с кнопкой сразу после запуска
    # application.post_init(send_initial_message)

    # application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

       # добавление обработчиков
    application.add_handler(CommandHandler("start", start, block=True))
    application.add_handler(MessageHandler(filters.TEXT, text, block=True))

    # добавляем CallbackQueryHandler (только для inline кнопок)
    application.add_handler(CallbackQueryHandler(button))

    # запуск бота (нажать Ctrl+C для остановки)
    application.run_polling()
    start()
    print('Бот остановлен')


if __name__ == "__main__":
    main()