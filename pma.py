"""
Copyright 2017 hackerftsg.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
"""

# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from queue import Queue
from time import sleep
from sys import stderr
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

try:
    from requests.exceptions import ConnectionError
    from requests import get
    from netaddr import IPRange
    from netaddr.core import AddrFormatError
except ImportError as error:
    exit("Package not found: %s" % error.message.split(" ")[-1])

def threader(arg0):
    """Method to run through threads"""
    while True:
        ip0, port0 = arg0.get().split(":")
        if isonline(ip0, int(port0)) and havepma(ip0, int(port0)):
            print >> stderr, "OK http://%s:%d/phpmyadmin/scripts/setup.php" % (ip0, int(port0))
        arg0.task_done()

def isonline(arg0, arg1):
    """Method to check if host is up and port 80 is open"""
    sock0 = socket(AF_INET, SOCK_STREAM)
    sock0.settimeout(0.5)
    return True if sock0.connect_ex((arg0, arg1)) == 0 else False

def havepma(arg0, arg1):
    """Method to check if host contains phpmyadmin installed"""
    try:
        return True if "donate to phpmyadmin" in get("http://%s:%d/phpmyadmin/scripts/setup.php" % (arg0, arg1), verify=False).text.lower() else False
    except ConnectionError:
        return False

def ipgenerate(arg0, arg1):
    """Method to return an array of 'ips' generated"""
    return [str(tmp0) for tmp0 in IPRange(arg0, arg1)]

disable_warnings(category=InsecureRequestWarning)

if __name__ == "__main__":
    try:
        print >> stderr, "AUTHOR hackerftsg"

        IP1 = raw_input("IP1 ")

        IP2 = raw_input("IP2 ")

        if not IP1 or not IP2:
            raise ValueError("ERROR Empty string")

        TMP1 = ipgenerate(IP1, IP2)

        TMP1 = [ip for ip in TMP1 if type(ip).__name__ == "str"]

        QUEUE = Queue()

        for index, ip in enumerate(TMP1):
            thread = Thread(target=threader, args=(QUEUE,))
            thread.daemon = True
            thread.start()

        for index, ip in enumerate(TMP1):
            QUEUE.put("%s:%d" % (ip, 80))
            sleep(0.3)

        QUEUE.join()

        print >> stderr, "For check if this bots are vulnerable, please use: python xpl.py <list>"

    except KeyboardInterrupt:
        print >> stderr, "ERROR KeyboardInterrupt detected"
    except AddrFormatError:
        print >> stderr, "ERROR, AddrFormatError detected"
    except ValueError as error:
        print >> stderr, error
