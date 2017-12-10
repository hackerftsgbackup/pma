"""
Copyright 2017 hackerftsg.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
"""

# -*- coding: utf-8 -*-

import sys
from os import system, path
from socket import socket, AF_INET, SOCK_STREAM
from urlparse import urlparse
from threading import Thread
from queue import Queue
from time import sleep
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

sys.dont_write_bytecode = True
disable_warnings(category=InsecureRequestWarning)

try:
    from requests.exceptions import ConnectionError
    from requests import get
    from netaddr import IPRange
    from netaddr.core import AddrFormatError
    from config import AD1, AD2
except ImportError as error:
    exit("Package not found: %s" % error.message.split(" ")[-1])

def threader_url(arg0):
    """Method to run through threads"""
    while True:
        url0 = arg0.get()
        system("title SCANNING %s" % url0)
        if havepma1(url0):
            print >> sys.stderr, "OK %s" % url0
        arg0.task_done()

def threader_ip(arg0):
    """Method to run through threads"""
    while True:
        ip0, port0 = arg0.get().split(":")
        system("title SCANNING http://%s:%d/phpmyadmin/scripts/setup.php" % (ip0, int(port0)))
        if iponline(ip0, int(port0)) and havepma0(ip0, int(port0)):
            print >> sys.stderr, "OK http://%s:%d/phpmyadmin/scripts/setup.php" % (ip0, int(port0))
        arg0.task_done()

def iponline(arg0, arg1):
    """Method to check if host is up and port 80 is open"""
    sock0 = socket(AF_INET, SOCK_STREAM)
    sock0.settimeout(0.5)
    return True if sock0.connect_ex((arg0, arg1)) == 0 else False

def havepma0(arg0, arg1):
    """Method to check if host contains phpmyadmin installed"""
    try:
        return True if "donate to phpmyadmin" in get("http://%s:%d/phpmyadmin/scripts/setup.php" % (arg0, arg1), verify=False).text.lower() else False
    except ConnectionError:
        return False

def havepma1(arg0):
    """Method to check if url contains phpmyadmin installed"""
    try:
        return True if "donate to phpmyadmin" in get(arg0, verify=False).text.lower() else False
    except ConnectionError:
        return False

def ipgenerate(arg0, arg1):
    """Method to return an array of 'ips' generated"""
    return [str(tmp0) for tmp0 in IPRange(arg0, arg1)]

if __name__ == "__main__":
    try:
        print >> sys.stderr, "AUTHOR hackerftsg"

        ARGS = sys.argv
        URLS = []

        for index, arg in enumerate(ARGS):
            if arg == "-pma":
                urls = ARGS[index + 1 if len(ARGS) >= 3 else index]
                if path.exists(urls) and path.isfile(urls):
                    for line in open(urls).readlines():
                        URLS.append(line)

        if len(URLS) < 1:
            if not AD1 or not AD2:
                raise ValueError("ERROR Empty string")

            TMP1 = ipgenerate(AD1, AD2)

            TMP1 = [ip for ip in TMP1 if type(ip).__name__ == "str"]

            QUEUE = Queue()

            for index, ip in enumerate(TMP1):
                thread = Thread(target=threader_ip, args=(QUEUE,))
                thread.daemon = True
                thread.start()

            for index, ip in enumerate(TMP1):
                QUEUE.put("%s:%d" % (ip, 80))
                sleep(0.3)

            QUEUE.join()
        else:
            URLS = [url for url in URLS if bool(urlparse(url).scheme)]

            QUEUE = Queue()

            for index, url in enumerate(URLS):
                thread = Thread(target=threader_url, args=(QUEUE,))
                thread.daemon = True
                thread.start()

            for index, url in enumerate(URLS):
                QUEUE.put(url)
                sleep(0.3)

            QUEUE.join()

        print >> sys.stderr, "For check if this bots are vulnerable, please use: python xpl.py <list>"

    except KeyboardInterrupt:
        print >> sys.stderr, "ERROR KeyboardInterrupt detected"
    except AddrFormatError:
        print >> sys.stderr, "ERROR, AddrFormatError detected"
    except ValueError as error:
        print >> sys.stderr, error
