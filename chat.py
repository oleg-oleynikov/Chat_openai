from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import hbold

import openai_secret_manager
import openai
import re

BOT_TOKEN = BOT_TOKEN
openai.api_key = API_TOKEN

class ChatState(StatesGroup):
    waiting_for_text = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        text="Привет! Напиши вопрос или задачу\n\n/new - Начать новый диалог\n/continue - Продолжить генерацию текста")
        
       
@dp.message_handler(commands=['continue'])
async def continue_generation(message, state=None):
    await message.delete()

    async with state.proxy() as data:
        if 'text' in data:
            data['text'] = data['text'] + ".Представь что ты специалист в этой сфере и напиши как можно больше об этом, на 3000 символов"
            data['text'] = await generate_text(data['text'])
            await message.answer(text=data['text'])
            await message.answer(text="Генерация окончена")
            data['text'] = None
        else:
            pass



@dp.message_handler(commands=['new'])
async def reset_conv(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text="Начат новый диалог")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(text="/new - Начать новый диалог\n/continue - Продолжить генерацию текста")
    
    
    
@dp.message_handler(state=None)
async def answer_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        prompt = data['text'] + ".Напиши об этом как можно больше и на все возможные токены, также если мысль была не закончена напиши в конце '/continue', или ты можешь её продолжить написав что то еще по этой теме напиши в конце '/continue'"
        await message.answer(text=await generate_text(prompt))


async def generate_text(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=3400,
            n=1,
            stop=None,
            temperature=0.5,
        )

        message = response.choices[0].text.strip()
        message = re.sub(r'\n\n+', '\n\n', message)
        return message
    except Exception as e:
        print(e)
        return "Произошла ошибка при генерации текста"


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)  
