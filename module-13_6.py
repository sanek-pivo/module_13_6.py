from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


kb1 = InlineKeyboardMarkup()
kb2 = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
button_3 = InlineKeyboardButton(text='Информация', callback_data='info')
kb1.add(button_1)
kb1.add(button_2)
kb2.add(button_3)


@dp.message_handler(commands='start')
async def start(message):
    await message.answer(f'Привет! Я бот помогающий Вашему здоровью.\n'
                         f'Чтобы начать, введите "Рассчитать"')


@dp.message_handler(text='Рассчитать')
async def set_age(message):
    await message.answer('Выберите опцию:', reply_markup=kb1)


@dp.callback_query_handler(text='formulas')
async def info(call):
    await call.message.answer(f'10 * вес(кг) + 6.25 * рост(см) - 5 '
                              f'* возраст(лет) + 5 для мужчин\n10 * '
                              f'вес(кг) + 6.25 * рост(см) - 5 * '
                              f'возраст(лет) - 161 для женщин',
                              reply_markup=kb1)
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories_m = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_w = 10 * weight + 6.25 * growth - 5 * age - 161

    global a
    global g
    global w
    global c_m
    global c_w
    a = age
    g = growth
    w = weight
    c_m = calories_m
    c_w = calories_w
    await message.answer('Расчёт произведён, посмотрите информацию', reply_markup=kb2)

    @dp.callback_query_handler(text='info')
    async def info(call):
        await call.message.answer(f'Ваш возраст:  {a}\nВаш рост:      {g}\nВаш вес:          {w}\n'
                                  f'Ваша норма калорий: {c_m}, если вы мужчина\n    '
                                  f'                                      {c_w}, если вы женщина', reply_markup=kb1)
        await call.answer()

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)