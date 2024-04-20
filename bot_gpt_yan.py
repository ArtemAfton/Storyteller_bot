import telebot
#from config_template import text1
import time
from config_template import IAM_TOKEN, FOLDER_ID, GPT_MODEL, CONTINUE_STORY, END_STORY, SYSTEM_PROMPT
import requests
from telebot.types import ReplyKeyboardMarkup
#from yan_gpt import count_all_tokens

token = "Your Token"
bot = telebot.TeleBot(token)

user_data = {
    "id": "",
    "genre": "",
    "character": "",
    "location": "",
}

def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

def gg(message):
    pass
def gg1(message):
    pass
def gg2(message):
    pass
def gg3(message):
    pass
def gg4(message):
    pass

def gg5(message):
    pass

def ask_gpt(collection, mode='continue'):
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 100
        },
        "messages": []
    }

    for row in collection:
        content = row['content']

        # Добавь дополнительный текст к сообщению пользователя в зависимости от режима
        if mode == 'continue' and row['role'] == 'user':
            content += f'\n{CONTINUE_STORY}'
        elif mode == 'end' and row['role'] == 'user':
            content += f'\n{END_STORY}'

        data["messages"].append(
                {
                    "role": row["role"],
                    "text": content
                }
            )

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            result = f"Status code {response.status_code}"
            return result
        result = response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."
    return result

def create_system_prompt(data, user_id):
    prompt = SYSTEM_PROMPT

    prompt += (f'\nНапиши историю в жанре {user_data["genre"]}'
               f' с главным героем: {user_data["character"]}. '
               f'Дело происходит в {user_data["location"]}. Начало должно быть коротким, не более 3х предложений.'
               f'   Не пиши никакой пояснительный текст от себя')
    return prompt


@bot.message_handler(commands=["start"])
def start_message(message):
    user_data["id"] = message.from_user.id
    bot.send_message(message.chat.id, f"Да-да, {message.from_user.full_name}, это новый бот от Fazbear Ent, который "
                                      f"поможет вам сгенерировать похожие крутые истории! Скорее попробуйте!")
    time.sleep(3)
    bot.send_message(message.chat.id, "Только сначала зполните некоторые настройки, чтобы помочь нам составить самую "
                                      "крутую историю на свете!")
    time.sleep(1)
    bot.send_message(message.chat.id, "В каком жанре вы хотите историю?",
                     reply_markup=create_keyboard(["Хорор", "Драма", "Комедия"]))
    bot.register_next_step_handler(message, genre)

@bot.message_handler(content_types=["text"], func=gg)
def genre(message):
    user_data["genre"] = message.text
    bot.send_message(message.chat.id, "Принято! В каком месте будут происходить действия?",
                     reply_markup=create_keyboard(["Пиццерия", "Подвал", "Квартира"]))
    bot.register_next_step_handler(message, location)

@bot.message_handler(content_types=["text"], func=gg1)
def location(message):
    user_data["location"] = message.text
    #location = user_data["location"]
    bot.send_message(message.chat.id, "Понятно. А теперь опиши своего персонажа.",
                     reply_markup=create_keyboard(["Бесстрашный и отважный", "Депрессивный и угнетённый", "Наглый и дерзкий"]))
    bot.register_next_step_handler(message, character)

@bot.message_handler(content_types=["text"], func=gg2)
def character(message):
    user_data["character"] = message.text
    #character = user_data["character"]
    bot.send_message(message.chat.id, "Напиши начало истории")
    bot.register_next_step_handler(message, creating_story)


@bot.message_handler(content_types=["text"], func=gg3)
def creating_story(message):
    global user_collection
    global user_id
    user_id = message.from_user.id
    genre = user_data["genre"]
    character = user_data["character"]
    location = user_data["location"]

    user_data1 = {
        user_id: {
            "genre": genre,
            "character": character,
            "locarion": location

        }
    }

    user_collection = {
        user_id: [
            {'role': 'system', 'content': create_system_prompt(user_data, user_id)},
        ]
    }
#
    user_content = message.text
    user_collection[user_id].append({'role': 'user', 'content': user_content})
    assistant_content = ask_gpt(user_collection[user_id])
    bot.send_message(message.chat.id, assistant_content)
    bot.send_message(message.chat.id, "Напиши 'продолжить', если хочешь ещё. Напиши end, если хочешь закончить")
    bot.register_next_step_handler(message, choose)
    user_collection[user_id].append({'role': 'assistant', 'content': assistant_content})

    #tokens = count_all_tokens(assistant_content)
    #bot.send_message(message.chat.id, tokens)

def choose(message):
    if message.text == "end":
        bot.register_next_step_handler(message, ending)
    elif message.text != "end":
        bot.register_next_step_handler(message, continuing)

@bot.message_handler(content_types=["text"], func=gg4)
def continuing(message):
    assistant_content = ask_gpt(user_collection[user_id], "continue")
    bot.send_message(message.chat.id, assistant_content)
    bot.send_message(message.chat.id, "Напиши 'продолжить', если хочешь большего. Напиши end, если хочешь закончить")
    user_collection[user_id].append({'role': 'assistant', 'content': assistant_content})
    bot.register_next_step_handler(message, choose)
@bot.message_handler(content_types=["text"], func=gg5)
def ending(message):
    assistant_content = ask_gpt(user_collection[user_id], 'end')
    user_collection[user_id].append({'role': 'assistant', 'content': assistant_content})
    bot.send_message(message.chat.id, "Вот что у нас получилось:")
    for one_mess in user_collection[user_id]:
        bot.send_message(message.chat.id, one_mess['content'])





bot.polling()