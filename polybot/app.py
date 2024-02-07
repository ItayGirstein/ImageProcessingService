import flask
from flask import request
import os
from bot import ObjectDetectionBot
from pyngrok import ngrok

app = flask.Flask(__name__)


def get_ngrok():
    auth_token = os.environ['NGROK_TOKEN']
    ngrok.set_auth_token(auth_token)
    http_tunnel = ngrok.connect(8443,'http')
    return http_tunnel.data['public_url']


TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_APP_URL = get_ngrok()


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
    # docker run -it --rm -p 8443:8443 -e TELEGRAM_TOKEN='6618070415:AAGhQx8LAkajaXxWB8rsW3MsFArijgUmdTo' -e NGROK_TOKEN='2TcY0NHwefU2mwH5b63mFEZW4mt_6si6nEdzFYbLR9ikG2a9i' -e BUCKET_NAME='itay9413-bucket' -v $HOME/.aws/credentials:/root/.aws/credentials:ro --name 'tele_con' --network mongoCluster 'my-tele-bot'
