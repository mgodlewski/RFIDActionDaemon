import unittest
from mock import patch, Mock, MagicMock
import datetime

class EventManagerSpy:
    def __init__(self):
        self.received_events = []
    def notify(self, uid, duration):
        self.received_events.append((uid, duration))

class TestRfidListener(unittest.TestCase):

    def setUp(self):
        import sys
        self.pirc522_mock = MagicMock()
        self.time_mock = MagicMock()
        a_time = datetime.datetime(2017, 10, 26, 20, 45, 56)
        self.time_mock.time.side_effect = [ a_time
                                        , a_time + datetime.timedelta(seconds=1)
                                        , a_time + datetime.timedelta(seconds=2)
                                        , a_time + datetime.timedelta(seconds=3)
                                        , a_time + datetime.timedelta(seconds=4)
                                        , a_time + datetime.timedelta(seconds=5)
                                        , a_time + datetime.timedelta(seconds=6)
                                        , a_time + datetime.timedelta(seconds=7)]
        modules = { 'pirc522': self.pirc522_mock,
                    'time': self.time_mock }
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from rfid_daemon import RfidListener
        self.tested = RfidListener()

    def tearDown(self):
        self.module_patcher.stop()

    def test_same_uid_for_2_seconds(self):
        self.pirc522_mock.RFID.return_value.wait_for_tag()
        self.pirc522_mock.RFID.return_value.request.return_value = ( None, "data")
        self.pirc522_mock.RFID.return_value.anticoll.side_effect = [( None, "uid12"), ( None, "uid12"), ( None, "uid12"), ( None, "exit")]

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('uid12', 0))
        self.assertEqual(spy.received_events.pop(0), ('uid12', 1))
        self.assertEqual(spy.received_events.pop(0), ('uid12', 2))

    def test_a_uid_then_another_uid(self):
        self.pirc522_mock.RFID.return_value.wait_for_tag()
        self.pirc522_mock.RFID.return_value.request.return_value = ( None, "data")
        self.pirc522_mock.RFID.return_value.anticoll.side_effect = [( None, "a_uid"), ( None, "another_uid"), ( None, "exit")]

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        self.assertEqual(spy.received_events.pop(0), ('another_uid', 0))
        
    def test_a_uid_then_nothing_for_3_seconds_then_the_same_uid(self):
        a_time = datetime.datetime(2017, 10, 26, 20, 45, 56)
        self.time_mock.time.side_effect = [ a_time
                                        , a_time + datetime.timedelta(seconds=4)
                                        , a_time + datetime.timedelta(seconds=5)]
        self.pirc522_mock.RFID.return_value.wait_for_tag()
        self.pirc522_mock.RFID.return_value.request.return_value = ( None, "data")
        self.pirc522_mock.RFID.return_value.anticoll.side_effect = [( None, "a_uid"), ( None, "a_uid"), ( None, "exit")]

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        


if __name__ == '__main__':
    unittest.main()
