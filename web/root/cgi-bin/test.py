#!/usr/bin/env python

import multiprocessing
import pycurl
import StringIO


URLS = ['http://192.168.1.173/sensors', 'http://192.168.1.175/sensors', 'http://192.168.1.179/cgi-bin/sensors']

def get_content(url):
    buf = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt( pycurl.WRITEFUNCTION, buf.write )
    c.perform()
    c.close()
    try:
	return buf.getvalue()
    except:
	return "Error!"

pool = multiprocessing.Pool(processes=8)  # play with ``processes`` for best results
results = pool.map(get_content, URLS) # This line blocks, look at map_async 
                                      # for non-blocking map() call
pool.close()  # the process pool no longer accepts new tasks
pool.join()   # join the processes: this blocks until all URLs are processed

for result in results:
    print result
