import unittest
from parsers import *
from models import *
from triage import *


class ParserTests(unittest.TestCase):
    def test_parse(self):
        model = response_model_from_yaml(
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
            """
        )
        user = model.build('test')
        self.assertEqual(user.get_response('Help!'), 'Message 1. Send an integer!')
        self.assertEqual(user.get_response('not a number'), retry_message)
        self.assertEqual(user.get_response('1'), 'Message 2. Send a string!')
        self.assertEqual(user.get_response('a string'), Actions.stop)


class QueryTests(unittest.TestCase):
    def test_get_hospital_info(self):
        data = get_hospital_records_in_zip_codes(['92866', '92680'])
        self.assertTrue(len(data) > 0)
        self.assertIsNotNone(make_hospital_choice(data))


if __name__ == '__main__':
    unittest.main()
