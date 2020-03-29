import models, logging, yaml, enum, parsers, collections, threading, time, triage, matching.match_users
from flask import Flask, make_response, render_template, redirect, url_for, request, session
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from waitress import serve
import sys


application = Flask(__name__)
application.config.from_object(__name__)

user_model_repo = models.UserModelRepository(parsers.response_model_from_yaml_file('schema.yaml'), logging.getLogger(str(__name__)))
user_queue = collections.deque()
to_respond_queue = collections.deque()
lock = threading.RLock()
work_available_condition = threading.Condition(lock)


credentials = yaml.safe_load(open('./configuration.yml'))
twilio_acct_sid = credentials['twilio']['acct_sid']
twilio_token = credentials['twilio']['token']
twilio_number = credentials['twilio']['number']
twilio_service_sid = credentials['twilio']['msg_service_sid']

application.secret_key = credentials['flask']['secret_key']

zip_code_api_key = credentials['zipcodeapi']['api_key']
zip_code_radius = int(credentials['zipcodeapi']['radius'])


client = Client(twilio_acct_sid, twilio_token)

# Not needed?
# Triages = enum.Enum('Triages', ['requeue'])

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
        return render_template('no_users_index.html')


@application.route('/sms', methods=['POST'])
def sms():
    phone_number = request.values.get('From', None)
    message_body = request.values.get('Body', None).strip()
    if message_body.upper() == 'RESTART':
        user_model_repo.delete(phone_number)
    resp = MessagingResponse()
    response, cont = user_model_repo.get_response(phone_number, message_body)
    resp.message(response)
    if not cont:
        user_queue.append(user_model_repo.users[phone_number])
    return str(resp)


@application.route('/verdict', methods=['POST'])
def verdict():
    session['user_uuid'] = None
    session['user_vals'] = None

    triage_code = request.values.get('triages', None)
    user_number = request.values.get('phonenumber', None)
    # TODO: make these messages easier to customize

    triage_instructions, get_hospital_location = get_triage_instructions(triage_code)
    if triage_instructions is None:
        # todo: fix edge case of 'awkward rematching'
        user_queue.appendleft(user_model_repo.users[user_number])
    else:
        user = user_model_repo.get_or_create(user_number)
        user.values['phone_number'] = user_number
        user.values['triage_code'] = triage_code
        user.values['triage_instructions'] = triage_instructions
        user.values['get_hospital'] = get_hospital_location
        with work_available_condition:
            to_respond_queue.append(user)
            work_available_condition.notify()
        user_model_repo.delete(user_number)

    return render_template('verdict.html')


def get_triage_instructions(triage_code):
    # TODO: make triage codes conform to levels of care in matching, and expand on these options
    if triage_code == 'home':
        triage_instructions = "Stay at home, rest, and take medication as necessary"
        return triage_instructions, False
    elif triage_code == 'triage1' or triage_code == 'triage2' or triage_code == 'triage3' or triage_code == 'triage4':
        triage_instructions = "Go to the ER ASAP"
        return triage_instructions, True
    elif triage_code == 'gettest':
        triage_instructions = "You should be tested for COVID-19 at the nearest testing location", False
        return triage_instructions, False
    elif triage_code == 'checkinlater':
        triage_code = "Please stay put and text back in 8 hours"
        return triage_instructions, False 
    else:
        return None, None


def create_api_query_worker_thread():
    def do_work():
        while True:
            with work_available_condition:
                try:
                    user = to_respond_queue.popleft()
                    while True:  # perform API calls (may fail)
                        try:
                            instructions = user.values['triage_instructions']
                            if user.values['get_hospital']:
                                user_zip_code = user.values['zip_code']
                                all_zip_codes = triage.get_zip_codes_in_radius(user_zip_code, zip_code_radius, zip_code_api_key)
                                hospitals = triage.get_hospital_records_in_zip_codes(all_zip_codes)
                                weights = matching.match_users.get_match_weights(user_zip_code, user.values['triage_code'],
                                                                                 hospitals)
                                selected_hospitals = triage.make_hospital_choice(hospitals, weights)
                                instructions += f'\n\nPlease choose one of the following care centers:\n '
                                for hosp in selected_hospitals:
                                    instructions += \
                                                f'{hosp["attributes"]["NAME"]} \n ' + \
                                                f'{hosp["attributes"]["ADDRESS"]} \n ' + \
                                                f'{hosp["attributes"]["CITY"]}, ' + \
                                                f'{hosp["attributes"]["STATE"]}  ' + \
                                                f'{hosp["attributes"]["ZIP"]}\n\n'
                            client.messages.create(from_=twilio_number, body=instructions, to=user.values['phone_number'])
                            break
                        except ValueError as ve:
                            print('Error: {}'.format(ve), file=sys.stderr)
                            time.sleep(1)  # sleep for one second before trying again
                        except KeyError as ke:
                            print('Value not found: {}'.format(ke.with_traceback()), file=sys.stderr)
                            break
                except:
                    work_available_condition.wait()

    return threading.Thread(target=do_work, daemon=True)



if __name__ == '__main__':
    api_threads = [create_api_query_worker_thread() for i in range(1)]
    for thr in api_threads:
        thr.start()

    if credentials['flask']['debug'] == True:
        application.run( host=credentials['flask']['host'], port=int(credentials['flask']['port']), debug=True)
    else:
        serve(application, host=credentials['flask']['host'], port=int(credentials['flask']['port']))