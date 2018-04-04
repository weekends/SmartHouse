#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
def set_output_encoding(codec, errors='strict'):
    import io, sys
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), errors=errors,
            line_buffering=sys.stdout.line_buffering)
set_output_encoding('utf8')


from html import escape
import cgi

def application(environ, start_response):
	#remote = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
	#port = -1
	#if 'port' in remote:
	#	port = remote.get_first('port')

	#form = cgi.FieldStorage()
	#mystr = ("<p>Port: %s == %s<br>" % (form["port"].value, form["state"].value))


	#mystr = "Test<br>"+str(environ)+'<br>'
	form = cgi.FieldStorage(environ=environ)
	mystr = "Test<br>"+str( form["port"] )+"<br>"

	for key in form.keys():
		mystr += key+"<br>"

	envvar = ['%s=%s' % (key, value) for key, value in sorted(environ.items())]


	body = ('<html><head><meta charset="utf-8" /></head><body><h2>h€lló wörld (python3 fcgi)</h2><pre>'+ mystr + escape('\n'.join(envvar)) + '</pre></body></html>').encode()
	status = '200 OK'
	headers = [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(body)))]
	start_response(status, headers)

	return [body]

if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()
