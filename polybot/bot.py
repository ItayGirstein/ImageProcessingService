import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import boto3
import requests
import json

BUCKET_NAME = os.environ['BUCKET_NAME']
s3 = boto3.client("s3")


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)

            # TODO upload the photo to S3
            img_name = os.path.basename(photo_path).split('/')[-1]
            try:
                s3.upload_file(photo_path, BUCKET_NAME, img_name)
            except Exception as e:
                print(f'Error: {e}')
            # TODO send a request to the `yolo5` service for prediction
            url = "http://yolo_con:8081/predict"
            args = {'imgName': img_name}
            r = requests.post(url=url, params=args)
            # TODO send results to the Telegram end-user
            if r.status_code == 200:
                predict = json.loads(r.text)
                labels = predict['labels']
                objects = {}
                data = ''
                for d in labels:
                    clas = d['class']
                    if clas not in objects:
                        objects[clas] = 1
                    else:
                        objects[clas] += 1
                for clas, times in objects.items():
                    data = data + '\n' + clas + ': ' + str(times)

                self.send_text(msg['chat']['id'], "Detected objects:" + data)

            else:
                self.send_text(msg['chat']['id'], "Exited with status code: " + str(r.status_code))
        else:
            self.send_text(msg['chat']['id'], "I'm waiting for an image...")
