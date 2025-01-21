from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from states import Form, Form_2

from aiogram.fsm.context import FSMContext

import requests

router = Router()




def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None




# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, users: dict):
    #users[str(message.from_user.id)] = 'Проверка сервиса'
    await message.reply(f"Добро пожаловать! Я ваш бот.\nВаш id: {message.from_user.id}. Вот, что я умею: \n/start \n/set_profile.\n/log_water <выпито мл воды>\n/log_food <название продукта>\n/log_workout <тип тренировки> <время (мин)>\n/check_progress\n/weather_in_MSC\n")



"""
users = {
    "user_id": {
        "weight": 80,
        "height": 184,
        "age": 26,
        "activity": 45,
        "city": "Paris",
        "water_goal": 2400,
        "calorie_goal": 2500,
        "logged_water": 500,
        "logged_calories": 1800,
        "burned_calories": 400
    }
}

"""



@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext, users: dict):
    if str(message.from_user.id) not in users:
        users[str(message.from_user.id)] = dict()
        users[str(message.from_user.id)]["logged_water"] = []
        users[str(message.from_user.id)]["logged_calories"] = []
        users[str(message.from_user.id)]["burned_calories"] = []
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Form.activities)


@router.message(Form.activities)
async def process_ativities(message: Message, state: FSMContext):
    await state.update_data(activities=message.text)
    await message.reply("В каком городе вы находитесь? Укажите на английском языке.")
    await state.set_state(Form.city)


@router.message(Form.city)
async def process_city(message: Message, state: FSMContext, users: dict, weather_api_key: str):
    await state.update_data(city=message.text)
    data = await state.get_data()
    try:
        weight = float(data.get("weight"))
        height = float(data.get("height"))
        age = float(data.get("age"))
        activities = float(data.get("activities"))
    except:
        await message.reply(f"Вы ввели нечисловые данные для веса, роста, возраста или активностей. Попробуйте ещё раз /set_profile.")
        await state.clear()


    city = data.get("city")

    # попробуем узнать погоду в городе
    url = "http://api.openweathermap.org/data/2.5/weather?" + "appid=" + weather_api_key + "&q="
    url = url + city
    try:
        response = requests.get(url)
        x = response.json()
        if x["cod"] == 200:
            y = x["main"]
            temp = y["temp"] - 273.15
        else:
            temp = 0
    except:
        temp = 0

    users[str(message.from_user.id)]['weight'] = weight
    users[str(message.from_user.id)]['height'] = height
    users[str(message.from_user.id)]['age'] = age
    users[str(message.from_user.id)]['activity'] = activities
    users[str(message.from_user.id)]['city'] = city

    #"water_goal"
    # Вес×30мл/кг + 500мл за каждые 30 минут активности.  +500−1000мл за жаркую погоду (> 25°C)
    hot = 0
    if temp > 25:
        hot = 700
    users[str(message.from_user.id)]['water_goal'] = weight*30 + 500*activities/30 + hot

    #"calorie_goal"
    # 10×Вес (кг)+6.25×Рост (см)−5×Возраст
    users[str(message.from_user.id)]['calorie_goal'] = 10*weight + 6.25*height - 5*age

    await message.reply(f"Привет! Тебе {age} лет. Твой рост: {height} см. Вес: {weight} кг.\nТвоя активность в день: {activities} минут. Ты из города {city}.\nЦель по воде на сутки: {users[str(message.from_user.id)]['water_goal']} мл. \nЦель по калориям на сутки: {users[str(message.from_user.id)]['calorie_goal'] }.")
    await state.clear()






# Обработчик команды /weather_in_MSC
@router.message(Command("weather_in_MSC"))
async def cmd_weather_in_MSC(message: Message, users: dict, weather_api_key: str):
    url = "http://api.openweathermap.org/data/2.5/weather?" + "appid=" + weather_api_key + "&q="
    url = url + 'Moscow'
    response = requests.get(url)
    x = response.json()
    answer = ''
    if x["cod"] == 200:
        y = x["main"]
        temp = y["temp"] - 273.15
        await message.reply(f"Погода в Москве: {temp} ℃.")
    else:
        await message.reply(f"Не могу узнать погоду в вашем городе!")


#Команда /log_water <количество>:
#Сохраняет, сколько воды выпито.
#Показывает, сколько осталось до выполнения нормы.
@router.message(Command("log_water"))
async def cmd_log_water(message: Message, users: dict):
    if str(message.from_user.id) not in users:
        users[str(message.from_user.id)] = dict()
        users[str(message.from_user.id)]["logged_water"] = []
        users[str(message.from_user.id)]["logged_calories"] = []
        users[str(message.from_user.id)]["burned_calories"] = []
    try:
        drinken = float(message.text.split()[1])
    except:
        await message.reply("Неверный формат ввода команды. Попробуйте ввести '/' + 'log_water' + 'выпито воды в мл'.")


    users[str(message.from_user.id)]["logged_water"].append(drinken)



    if 'water_goal' not in users[str(message.from_user.id)]:
        await message.reply(f"Цель по воде не установлена. Выполните: /set_profile")
    else:
        goal = users[str(message.from_user.id)]['water_goal']
        drinken = sum(users[str(message.from_user.id)]["logged_water"])

        if goal <= drinken:
            await message.reply(f"Цель по воде выполнена. План: {goal}. Выпито: {drinken}.")
        else:
            await message.reply(f"До выполнения нормы осталось выпить {goal-drinken} мл.")






# Команда /log_food <название продукта>
@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext, users: dict):
    if str(message.from_user.id) not in users:
        users[str(message.from_user.id)] = dict()
        users[str(message.from_user.id)]["logged_water"] = []
        users[str(message.from_user.id)]["logged_calories"] = []
        users[str(message.from_user.id)]["burned_calories"] = []

    try:
        product = message.text.split()[1]
        await state.set_state(Form_2.product)
        await state.update_data(product=product)
    except:
        await message.reply("Неверный формат ввода команды. Попробуйте ввести '/' + 'log_food' + 'название продукта на английском языке'.")

    await message.reply("Введите массу продукта в граммах:")
    await state.set_state(Form_2.weight)

@router.message(Form_2.weight)
async def process_pr_weight(message: Message, state: FSMContext, users: dict):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    try:
        weight = float(data.get("weight"))
        product = data.get("product")

        calories = get_food_info(product)
        if not calories:
            calories = 0
        else:
            cal = calories['calories']
            calories =  weight * calories['calories']/100

        users[str(message.from_user.id)]["logged_calories"].append(calories)

        await message.reply(f"{product} - {cal} ккал на 100 г. \nВы съели {weight} грамм.\nЗаписано: {calories} ккал.")
        await state.clear()



    except:
        await message.reply(f"Вы ввели нечисловые данные для массы продукта. Попробуйте ещё раз.")
        await state.clear()




#/log_workout <тип тренировки> <время (мин)>
@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, users: dict):
    if str(message.from_user.id) not in users:
        users[str(message.from_user.id)] = dict()
        users[str(message.from_user.id)]["logged_water"] = []
        users[str(message.from_user.id)]["logged_calories"] = []
        users[str(message.from_user.id)]["burned_calories"] = []



    try:
        cmd, training, minutes = message.text.split()
        minutes = float(minutes)
        calories =  minutes * 10
        users[str(message.from_user.id)]["burned_calories"].append(calories)
        extra_water = round(200 * minutes / 30, 2)
        if 'water_goal' in users[str(message.from_user.id)]:
            users[str(message.from_user.id)]['water_goal']+=extra_water
        
        await message.reply(f"{training} {minutes} минут — {calories} ккал. Дополнительно: выпейте {extra_water} мл воды.")

    except:
        await message.reply("Неверный формат ввода команды.")



#Команда /check_progress
@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message, users: dict):
    try:
        goal =  users[str(message.from_user.id)]["water_goal"]
        drinken =  sum(users[str(message.from_user.id)]["logged_water"])
        logged_calories =  sum(users[str(message.from_user.id)]["logged_calories"])
        calorie_goal = users[str(message.from_user.id)]["calorie_goal"]
        burned_calories =  sum(users[str(message.from_user.id)]["burned_calories"])

        await message.reply(f"Прогресс:\nВода:\n- Выпито: {drinken} мл из {goal} мл.\n- Осталось: {goal-drinken} мл.\n\n\nКалории:\n- Потреблено: {logged_calories} ккал из {calorie_goal} ккал.\n- Сожжено: {burned_calories} ккал.\n- Баланс: {logged_calories - burned_calories} ккал.\n")
        


    except:
        await message.reply("Не хватает данных для отображения прогресса. Введите данные.")
















