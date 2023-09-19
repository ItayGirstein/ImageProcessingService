import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot_v1.img_proc import Img


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


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        cap_que = ['Blur', 'Contour', 'Rotate', 'Segment', 'Salt and pepper', 'Concat']
        logger.info(f'Incoming message: {msg}')
        if not self.is_current_msg_photo(msg):
            self.send_text(msg['chat']['id'], "Hello there please send me a photo with one of the function below:")
            self.send_text(msg['chat']['id'], f'{cap_que[0]}, {cap_que[1]}, {cap_que[2]}, {cap_que[3]}, {cap_que[4]}, {cap_que[5]} (currently not working)')
        else:
            if msg["caption"] in cap_que:
                new_img = Img(self.download_user_photo(msg))
                if msg["caption"] == cap_que[0]:
                    new_img.blur()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                elif msg["caption"] == cap_que[1]:
                    new_img.contour()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                elif msg["caption"] == cap_que[2]:
                    new_img.rotate()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                elif msg["caption"] == cap_que[3]:
                    new_img.segment()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                elif msg["caption"] == cap_que[4]:
                    new_img.salt_n_pepper()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                elif msg["caption"] == cap_que[5]:
                    new_img.concat()
                    self.send_photo(msg['chat']['id'], new_img.save_img())
                else:
                    self.send_text(msg['chat']['id'], "Unknown function please try again")
                