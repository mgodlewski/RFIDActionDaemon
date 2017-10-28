import unittest
from mock import patch, Mock, MagicMock
import datetime

class EventManagerSpy:
    def __init__(self):
        self.received_events = []
    def notify(self, duration, uid):
        self.received_events.append((duration, uid))

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

    def tearDown(self):
        self.module_patcher.stop()

    def test_same_uid_for_2_seconds(self):
        from rfid_daemon import RfidListener
        tested = RfidListener()
        self.pirc522_mock.RFID.return_value.wait_for_tag()
        self.pirc522_mock.RFID.return_value.request.return_value = ( None, "data")
        #self.pirc522_mock.RFID.return_value.anticoll.return_value = ( None, "exit")
        self.pirc522_mock.RFID.return_value.anticoll.side_effect = [( None, "uid12"), ( None, "uid12"), ( None, "uid12"), ( None, "exit")]

        spy = EventManagerSpy()
        tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), (0, 'uid12'))
        self.assertEqual(spy.received_events.pop(0), (1, 'uid12'))
        self.assertEqual(spy.received_events.pop(0), (2, 'uid12'))


if __name__ == '__main__':
    unittest.main()
