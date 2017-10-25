#!/usr/bin/env python 

from pirc522 import RFID
import signal
import time
from subprocess import call
import os
import datetime


uids = {}
with open("uid2Actions.conf") as f:
    for line in f:
       key, action = line.split(None, 1)
       uid = bytes(map(int, key.split(',')))
       uids[uid] = action
       print uid
       print action

rdr = RFID()

time_threshold = 3
previous_uid = bytes([0])
previous_timestamp = time.time()

while True:
    # Wait for tag
    rdr.wait_for_tag()

    # Request tag
    (error, data) = rdr.request()
    if not error:

        (error, uid) = rdr.anticoll()
        if not error:
            # Print UID
            bytes_uid = bytes(uid)
            if bytes_uid != previous_uid or previous_timestamp + time_threshold < time.time():
              previous_uid = bytes_uid
              previous_timestamp = time.time()
              print datetime.datetime.fromtimestamp(time.time())
              print("\nCard read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])+","+str(uid[4]))
              if bytes_uid in uids:
                print (uids[bytes_uid]);
                #call(uids[bytes_uid].split())
                os.system(uids[bytes_uid])
              else:
                print("No command associated with this uid")
