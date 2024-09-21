import time
from os.path import join

import requests
import json
import enum

from settings import BASE_DIR


class FileType(enum.Enum):
    IMAGE = 'image'
    AUDIO = 'audio'
    VIDEO = 'video'


class WhatsappBot:
    IMG_PATH = join(BASE_DIR, 'files', '65535_53085864099_f6e5193e10_500_150_nofilter.jpg')
    VIDEO_PATH = join(BASE_DIR, 'files', '6548176-hd_1920_1080_24fps.mp4')
    AUDIO_PATH = join(BASE_DIR, 'files', 'cat-98721.mp3')

    def __init__(self, instance_id: str, api_token: str):
        self.instance_id = instance_id
        self.api_token = api_token

        self.send_message_url = f"https://7103.api.greenapi.com/waInstance{instance_id}/sendMessage/{api_token}"
        self.receive_message_url = f"https://7103.api.greenapi.com/waInstance{instance_id}/receiveNotification/{api_token}"
        self.delete_message_url = f"https://7103.api.greenapi.com/waInstance{instance_id}/deleteNotification/{api_token}/"
        self.send_location_url = f"https://7103.api.greenapi.com/waInstance{instance_id}/sendLocation/{api_token}"
        self.send_file_by_upload_url = f"https://7103.api.greenapi.com/waInstance{instance_id}/sendFileByUpload/{api_token}"

        self.handlers = {}

    def send_message(self, message: str, chat_id: str):
        payload = {
            "chatId": chat_id,
            "message": message
        }
        headers = {
            'Content-Type': 'application/json'
        }
        requests.post(self.send_message_url, headers=headers, data=json.dumps(payload))

    def send_file(self, chat_id: str, file_type: FileType):

        payload = {
            'chatId': chat_id
        }
        files = {
            FileType.IMAGE: [('file', ('image.jpg', open(
                self.IMG_PATH,
                'rb'), 'image/jpeg'))],

            FileType.AUDIO: [('file', (
                'audio.mp3', open(self.AUDIO_PATH, 'rb'),
                'audio/mp3'))],

            FileType.VIDEO: [('file', (
                'video.mp4',
                open(self.VIDEO_PATH, 'rb'),
                'video/mp4'))]
        }
        requests.post(self.send_file_by_upload_url, data=payload, files=files[file_type])

    def send_location(self, chat_id: str):
        payload = {
            "chatId": chat_id,
            "latitude": 12.3456789,
            "longitude": 10.1112131,
            "nameLocation": 'Restaurant',
            "address": "123456, Perm",
        }
        headers = {
            'Content-Type': 'application/json'
        }

        requests.post(self.send_location_url, headers=headers, data=json.dumps(payload))

    def check_new_messages(self):
        response = requests.get(self.receive_message_url)
        data = response.json()
        if response.status_code == 200 and data is not None:
            rec_id = data.get('receiptId')
            requests.delete(f'{self.delete_message_url}/{rec_id}')

            if data['body'].get('senderData') and data['body'].get('messageData'):
                return data
        return

    def register_handler(self, trigger: str):

        def decorator(func):
            self.handlers[trigger.lower()] = func
            return func

        return decorator

    def process_message(self, message_data: dict):
        body = message_data.get('body')
        msg_type = body.get('typeWebhook')
        if msg_type == 'incomingMessageReceived':
            name = body.get('senderData').get('chatName')
            chat_id = body.get('senderData').get('sender')
            message_text = body.get('messageData').get('textMessageData', {}).get('textMessage')

            print(f"Message from {name}(+{chat_id[:-5]}): {message_text}")

            if chat_id and message_text:
                trigger = message_text.lower()
                if self.handlers.get(trigger):
                    trigger_func = self.handlers[trigger]
                    trigger_func(chat_id)
                    return

                self.send_message("Команда не распознана", chat_id)

    def run(self, polling_interval: int = 1):
        print("Запуск...")
        try:
            while True:
                data = self.check_new_messages()

                if data is not None:
                    self.process_message(data)

                time.sleep(polling_interval)
        except KeyboardInterrupt:
            print("Бот отключен.")
