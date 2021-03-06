import unittest

from geolocation import GeoLocation
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
        self.assertEqual(user.get_response('not a number'), (retry_message.format('not a number'), True))
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
        self.assertEqual(repo.get_response('test', 'not a number'), (retry_message.format('not a number'), True))
        self.assertEqual(repo.get_response('test', '1'), ('Message 2. Send a string!', True))
        self.assertEqual(repo.get_response('test', 'a string'), ('Hello?', True))
        self.assertEqual(repo.get_response('test', 'hello'), ('You said hello!', False))

    def test_schema(self):
        model = response_model_from_yaml_text(test_yaml)
        user = model.build('test')
        self.assertEqual(user.get_response('Help!'), ('Welcome to Sequoia! What is your 5-digit ZIP code?', True))
        self.assertEqual(user.get_response('44116'), ('What is your temperature today? Answer 0 if you do not have a thermometer.', True))
        self.assertEqual(user.get_response('98.5'), ('Did you have or feel like you have had a fever in the last 24 hours? Y/N', True))
        self.assertEqual(user.get_response('Yes'), ('Do you have a new or worsening cough? Y/N', True))
        self.assertEqual(user.get_response('Yes'), ('Are you having trouble breathing? Y/N', True))
        self.assertEqual(user.get_response('Yes'), ('Do you have new or worsening body aches? Y/N', True))
        self.assertEqual(user.get_response('Yes'), ('Do you have a sore throat, different from your seasonal allergies? Y/N', True))
        self.assertEqual(user.get_response('Yes'), ('Hang tight, getting an expert opinion...', False))




class QueryTests(unittest.TestCase):

    def test_get_hospital_info(self):
        data = get_hospital_records_in_zip_codes(test_zip_codes)
        self.assertTrue(len(data) > 0)
        self.assertIsNotNone(make_hospital_choice(data))

    def test_get_hospital_info_bounding_box(self):
        data = get_hospital_records_within_distance('44116', 50)
        self.assertTrue(len(data) > 0)
        self.assertIsNotNone(make_hospital_choice(data))

    def test_hospital_weighting(self):
        weights = get_match_weights('44116', 'LEVEL 1', test_hospitals)
        self.assertEqual(len(weights), len(test_hospitals))
        choices = make_hospital_choice(test_hospitals, weights)
        self.assertIsNotNone(choices)
        # print(choices)

    def test_geolocation(self):
        loc1 = GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = GeoLocation.from_radians(loc1.rad_lat, loc1.rad_lon)
        self.assertTrue (loc1.rad_lat == loc2.rad_lat and loc1.rad_lon == loc2.rad_lon
                and loc1.deg_lat == loc2.deg_lat and loc1.deg_lon == loc2.deg_lon)

        # Test distance between two locations
        loc1 = GeoLocation.from_degrees(26.062951, -80.238853)
        loc2 = GeoLocation.from_degrees(26.060484, -80.207268)
        self.assertTrue (loc1.distance_to(loc2) == loc2.distance_to(loc1))

        # Test bounding box
        loc = GeoLocation.from_degrees(26.062951, -80.238853)
        distance = 1  # 1 kilometer
        SW_loc, NE_loc = loc.bounding_locations(distance)
        self.assertTrue(SW_loc.deg_lon < NE_loc.deg_lon and SW_loc.deg_lat < NE_loc.deg_lat)

if __name__ == '__main__':
    unittest.main()
