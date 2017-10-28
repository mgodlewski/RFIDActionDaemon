import time
import datetime
import os
from pirc522 import RFID

class EventManager:

    def notify(self, duration, uid):
        print datetime.datetime.fromtimestamp(time.time())
        print("\nCard read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])+","+str(uid[4]))
        print duration

class RfidListener:

    def __init__(self):
        self.rdr = RFID()
        self.time_threshold = 1

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
                    # Print UID
                    bytes_uid = bytes(uid)
                    if bytes_uid == "exit":
                        return;
                    current_time = time.time()
                    #return ( self.time_threshold, bytes_uid)
                    if bytes_uid != previous_uid :
                        previous_uid = bytes_uid
                        initial_timestamp = current_time
                        duration = 0
                        eventManager.notify(duration, bytes_uid)
                    else :
                        if current_time >= initial_timestamp + datetime.timedelta(seconds=duration + self.time_threshold):
                            duration += self.time_threshold
                            #print datetime.datetime.fromtimestamp(current_time)
                            #print("\nCard read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])+","+str(uid[4]))
                            eventManager.notify(duration , bytes_uid)
                        #if bytes_uid in uids:
                        #    print (uids[bytes_uid]);
                        #    #os.system(uids[bytes_uid])
                        #else:
                        #    print("No command associated with this uid")

