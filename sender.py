# -*- coding: utf-8 -*-

import urllib
import urllib2

def send(method, url, dictionary):
    # make a string with the request type in it:
    method = str(method)
    # create a handler. you can specify different handlers here (file uploads etc)
    # but we go for the default
    handler = urllib2.HTTPHandler()
    # create an openerdirector instance
    opener = urllib2.build_opener(handler)
    # build a request
    data = urllib.urlencode(dictionary)
    request = urllib2.Request(url, data=data)
    # add any other information you want
    request.add_header("Content-Disposition", 'form-data')
    # overload the get method function with a small anonymous function...
    request.get_method = lambda: method
    # try it; don't forget to catch the result
    try:
        connection = opener.open(request)
    except urllib2.HTTPError, e:
        connection = e

    # check. Substitute with appropriate HTTP code.
    if connection.code == 200:
        return False
    else:
        # handle the error case. connection.read() will still contain data
        # if any was returned, but it probably won't be of any use
        return e