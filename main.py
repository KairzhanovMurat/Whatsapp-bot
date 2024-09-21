from settings import Settings
from bot import WhatsappBot, FileType

settings = Settings()

bot = WhatsappBot(
    settings.instance_id,
    settings.api_token,

)


@bot.register_handler("Привет")
def handle_hello(chat_id: str):
    bot.send_message("Привет, введи 'start' для начала работы", chat_id)


@bot.register_handler("start")
def start_handler(chat_id: str):
    bot.send_message("Список доступных команд: \n"
                     "'1': Отправка  геолокации\n"
                     "'2': Отправка изображения\n"
                     "'3': Отправка видео\n"
                     "'4': Отправка аудио\n",
                     chat_id)


@bot.register_handler("1")
def location_sender(chat_id: str):
    bot.send_location(chat_id)


@bot.register_handler("2")
def image_sender(chat_id: str):
    bot.send_file(chat_id, FileType.IMAGE)


@bot.register_handler("3")
def video_sender(chat_id: str):
    bot.send_file(chat_id, FileType.VIDEO)


@bot.register_handler("4")
def audio_sender(chat_id: str):
    bot.send_file(chat_id, FileType.AUDIO)


if __name__ == "__main__":
    bot.run()
