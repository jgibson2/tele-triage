import unittest
from parsers import *
from models import *
from triage import *
from test_assets.test_assets import *
from matching.match_users import get_match_weights


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
        self.assertEqual(user.get_response('Help!'), ('Message 1. Send an integer!', True))
        self.assertEqual(user.get_response('not a number'), (retry_message, True))
        self.assertEqual(user.get_response('1'), ('Message 2. Send a string!', True))
        self.assertEqual(user.get_response('a string'), ('Hello?', True))
        self.assertEqual(user.get_response('hello'), ('You said hello!', False))

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
        self.assertEqual(repo.get_response('test', 'Help!'), ('Message 1. Send an integer!', True))
        self.assertEqual(repo.get_response('test', 'not a number'), (retry_message, True))
        self.assertEqual(repo.get_response('test', '1'), ('Message 2. Send a string!', True))
        self.assertEqual(repo.get_response('test', 'a string'), ('Hello?', True))
        self.assertEqual(repo.get_response('test', 'hello'), ('You said hello!', False))


class QueryTests(unittest.TestCase):

    def test_get_hospital_info(self):
        data = get_hospital_records_in_zip_codes(test_zip_codes)
        self.assertTrue(len(data) > 0)
        self.assertIsNotNone(make_hospital_choice(data))

    def test_hospital_weighting(self):
        weights = get_match_weights('44116', 'LEVEL 1', test_hospitals)
        self.assertEqual(len(weights), len(test_hospitals))
        choices = make_hospital_choice(test_hospitals, weights)
        self.assertIsNotNone(choices)
        # print(choices)

if __name__ == '__main__':
    unittest.main()
