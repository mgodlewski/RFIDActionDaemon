import datetime
import os

class EventManager:

    def __init__(self, confFile):
        self.uids = {}
        with open(confFile) as f:
            for line in f:
                key, action = line.split(None, 1)
                uid = bytes(map(int, key.split(',')))
                self.uids[uid] = action
                print("Conf: %-19s %s" % (uid, action))

    def notify(self, uid, duration):
        print datetime.datetime.now()
        print("\nCard read UID: %s" % uid)
        if uid in self.uids:
            print (self.uids[uid]);
            os.system(self.uids[uid])
        else:
            print("No command associated with this uid")

class NowBuilder:
    def now(self):
        return datetime.datetime.now()

class UidProvider:
    def __init__(self):
        from pirc522 import RFID
        self.rdr = RFID()

    def wait_for_uid(self):
        # Wait for tag
        self.rdr.wait_for_tag()
        # Request tag
        (error, data) = self.rdr.request()
        if not error:
            (error, uid) = self.rdr.anticoll()
            if not error:
                return bytes(uid)

class RfidListener:

    def __init__(self, uidProvider, nowBuilder):
        self.event_delta = 1
        self.reset_duration = 3
        self.uidProvider = uidProvider
        self.nowBuilder = nowBuilder
        self.initial_timestamp = self.nowBuilder.now()

    def listen(self, eventManager):
        previous_uid = None
        while True:
            bytes_uid = self.uidProvider.wait_for_uid()
            if bytes_uid == "exit":
                return;
            current_time = self.nowBuilder.now()
            if bytes_uid != previous_uid or current_time >= self.initial_timestamp + datetime.timedelta(seconds= self.reset_duration): 
                previous_uid = bytes_uid
                self.initial_timestamp = current_time
                duration = 0
                eventManager.notify(bytes_uid, duration)
            else :
                if current_time >= self.initial_timestamp + datetime.timedelta(seconds=duration + self.event_delta):
                    duration += self.event_delta
                    eventManager.notify(bytes_uid, duration)

if __name__ == "__main__":
    e = EventManager("uid2Actions.conf")
    RfidListener(UidProvider(), NowBuilder()).listen(e)
