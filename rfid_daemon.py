import datetime
import os
from pirc522 import RFID

class EventManager:

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

class RfidListener:

    def __init__(self, nowBuilder):
        self.rdr = RFID()
        self.event_delta = 1
        self.reset_duration = 3
        self.nowBuilder = nowBuilder

    def listen(self, eventManager):
        previous_uid = None
        while True:
            # Wait for tag
            self.rdr.wait_for_tag()
        
            # Request tag
            (error, data) = self.rdr.request()
            if not error:
        
                (error, uid) = self.rdr.anticoll()
                if not error:
                    bytes_uid = bytes(uid)
                    if bytes_uid == "exit":
                        return;
                    current_time = self.nowBuilder.now()
                    if bytes_uid != previous_uid or current_time >= initial_timestamp + datetime.timedelta(seconds= self.reset_duration): 
                        previous_uid = bytes_uid
                        initial_timestamp = current_time
                        duration = 0
                        eventManager.notify(bytes_uid, duration)
                    else :
                        if current_time >= initial_timestamp + datetime.timedelta(seconds=duration + self.event_delta):
                            duration += self.event_delta
                            eventManager.notify(bytes_uid, duration)

