import unittest
from parsers import *
from models import *
from triage import *


class ParserTests(unittest.TestCase):
    def test_parse(self):
        model = response_model_from_yaml_text(
            """
            - send:
                message: Message 1. Send an integer!
            - receive:
                key: number
                expect_type: int
                on_failure: retry
            - send:
                message: Message 2. Send a string!
            - receive:
                key: string
                expect_type: str
                on_failure: retry
            - send:
                message: Hello?
            - conditional:
                condition: message == 'hello'
                response_if_true:
                    - send:
                        message: You said hello!
                response_if_false:
                    - send:
                          message: You did not say hello :(
            """
        )
        user = model.build('test')
        self.assertEqual(user.get_response('Help!'), 'Message 1. Send an integer!')
        self.assertEqual(user.get_response('not a number'), retry_message)
        self.assertEqual(user.get_response('1'), 'Message 2. Send a string!')
        self.assertEqual(user.get_response('a string'), 'Hello?')
        self.assertEqual(user.get_response('hello'), 'You said hello!')
        self.assertEqual(user.get_response('should retrun stop'), Actions.stop)

    def test_user_model_repo(self):
        model = response_model_from_yaml_text(
            """
            - send:
                message: Message 1. Send an integer!
            - receive:
                key: number
                expect_type: int
                on_failure: retry
            - send:
                message: Message 2. Send a string!
            - receive:
                key: string
                expect_type: str
                on_failure: retry
            - send:
                message: Hello?
            - conditional:
                condition: message == 'hello'
                response_if_true:
                    - send:
                        message: You said hello!
                response_if_false:
                    - send:
                          message: You did not say hello :(
            """
        )
        repo = UserModelRepository(model)
        self.assertEqual(repo.get_response('test', 'Help!'), 'Message 1. Send an integer!')
        self.assertEqual(repo.get_response('test', 'not a number'), retry_message)
        self.assertEqual(repo.get_response('test', '1'), 'Message 2. Send a string!')
        self.assertEqual(repo.get_response('test', 'a string'), 'Hello?')
        self.assertEqual(repo.get_response('test', 'hello'), 'You said hello!')
        self.assertEqual(repo.get_response('test', 'should retrun stop'), Actions.stop)


class QueryTests(unittest.TestCase):
    def test_get_hospital_info(self):
        data = get_hospital_records_in_zip_codes(['92866', '92680'])
        self.assertTrue(len(data) > 0)
        self.assertIsNotNone(make_hospital_choice(data))


if __name__ == '__main__':
    unittest.main()
