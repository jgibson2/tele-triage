import models, logging, yaml, enum, parsers, collections
from flask import Flask, make_response, render_template, redirect, url_for, request, session
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

application = Flask(__name__)
application.config.from_object(__name__)

user_model_repo = models.UserModelRepository(parsers.response_model_from_yaml_file('schema.yaml'), logging.getLogger(str(__name__)))
user_queue = collections.deque()

credentials = yaml.load(open('./credentials.yml'))
twilio_acct_sid = credentials['twilio']['acct_sid']
twilio_token = credentials['twilio']['token']
twilio_number = credentials['twilio']['number']
twilio_service_sid = credentials['twilio']['msg_service_sid']

application.secret_key = credentials['flask']['secret_key']

client = Client(twilio_acct_sid, twilio_token)

Triages = enum.Enum('Triages', ['requeue'])

@application.route('/')
def home():
    if len(user_queue) > 0 or ('user_uuid' in session and session['user_uuid'] != None):
        if 'user_uuid' not in session or session['user_uuid'] == None:
            user = user_queue.popleft()
            session['user_uuid'] = user.uuid
            session['user_vals'] = user.values
        # display phone number, values, and triage options (including exit, re-queuing user)
        return render_template('index.html', values=session['user_vals'], phonenumber=session['user_uuid'])
    else:
        # todo: continuously check every few seconds
        return 'no users'

@application.route('/sms', methods=['POST'])
def sms():
    phone_number = request.values.get('From', None)
    message_body = request.values.get('Body', None)

    resp = MessagingResponse()
    
    response, cont = user_model_repo.get_response(phone_number, message_body)

    if cont:
        resp.message(response)
    else:
        user_queue.append(user_model_repo.users[phone_number])
    return str(resp)

@application.route('/verdict', methods=['POST'])
def verdict():
    triage_code = request.values.get('triages', None)
    user_number = request.values.get('phonenumber', None)
    triage_instructions = ""
    if triage_code == 'home':
        triage_instructions = "Stay at home, rest, and take medication as necessary"
    elif triage_code == 'er':
        triage_instructions = "Go to the ER ASAP"
    else:
        triage_instructions = "You have been placed back in the queue, and will be connected to a different doctor"
        # todo: fix edge case of 'awkward rematching' 
        user_queue.appendleft(user_model_repo.users[user_number])
    client.messages.create(from_=twilio_number, body=triage_instructions, to=user_number)
    session['user_uuid'] = None
    session['user_vals'] = None
    user_model_repo.delete(user_number)
    return render_template('verdict.html')

if __name__ == '__main__':
    application.run(host='127.0.0.1', port=5001, debug=True)