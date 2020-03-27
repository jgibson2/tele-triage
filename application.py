from flask import Flask, make_response

application = Flask(__name__)


@application.route('/')
def home():
    return make_response('OK', 200)


@application.route('/sms')
def home():
    return make_response('OK', 200)


if __name__ == '__main__':
    application.run()