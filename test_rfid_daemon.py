import unittest
from mock import patch, Mock, MagicMock
import datetime

class TestUidProvider(unittest.TestCase):

    def setUp(self):
        import sys
        self.pirc522_mock = MagicMock()
        modules = { 'pirc522': self.pirc522_mock }
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from rfid_daemon import UidProvider
        self.tested = UidProvider()

    def tearDown(self):
        self.module_patcher.stop()

    def test_wait_for_uid(self):
        self.pirc522_mock.RFID.return_value.wait_for_tag()
        self.pirc522_mock.RFID.return_value.request.return_value = ( None, "data")
        self.pirc522_mock.RFID.return_value.anticoll.return_value = ( None, "uid12")

        self.assertEqual(self.tested.wait_for_uid(), 'uid12')

class FakeNowBuilder:
    def program_now(self, delta_list):
        self.initial_datetime = datetime.datetime(2017, 10, 26, 20, 45, 56)
        self.delta_list = delta_list
    def now(self):
        return self.initial_datetime + datetime.timedelta(seconds=self.delta_list.pop(0))

class EventManagerSpy:
    def __init__(self):
        self.received_events = []
    def notify(self, uid, duration):
        self.received_events.append((uid, duration))

class FakeUidProvider:
    def program_wait_for_uid(self, uids):
        self.uids = uids
    def wait_for_uid(self):
        return self.uids.pop(0)

class TestRfidListener(unittest.TestCase):

    def setUp(self):
        from rfid_daemon import RfidListener
        self.fakeUidProvider = FakeUidProvider()
        self.fakeNowBuilder = FakeNowBuilder()
        self.fakeNowBuilder.program_now(range(0,8))
        self.tested = RfidListener(self.fakeUidProvider, self.fakeNowBuilder)

    def test_same_uid_for_2_seconds(self):
        self.fakeUidProvider.program_wait_for_uid(["uid12", "uid12", "uid12", "exit"])

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('uid12', 0))
        self.assertEqual(spy.received_events.pop(0), ('uid12', 1))
        self.assertEqual(spy.received_events.pop(0), ('uid12', 2))

    def test_a_uid_then_another_uid(self):
        self.fakeUidProvider.program_wait_for_uid(["a_uid", "another_uid", "exit"])

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        self.assertEqual(spy.received_events.pop(0), ('another_uid', 0))
        
    def test_a_uid_then_nothing_for_3_seconds_then_the_same_uid(self):
        self.fakeUidProvider.program_wait_for_uid(["a_uid", "a_uid", "exit"])
        self.fakeNowBuilder.program_now([0, 4, 5])

        spy = EventManagerSpy()
        self.tested.listen(spy)
        
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        self.assertEqual(spy.received_events.pop(0), ('a_uid', 0))
        


if __name__ == '__main__':
    unittest.main()
