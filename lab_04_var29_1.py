# py_ver == "3.6.9"
import flask
from flask import request

app = flask.Flask(__name__)

import time
import logging

logging.basicConfig(filename="/home/nikita/Desktop/secnotify.log",
                    level=logging.DEBUG,
                    format='%(asctime)s:%(module)s:%(name)s:%(levelname)s:%(message)s')
logging.debug("secnotify startup")
logger = logging.getLogger()


@app.after_request
def after_request(response):
    timestamp = time.strftime('[%Y-%b-%d %H:%M]')
    app.logger.error(
        '%s %s %s %s %s %s %s %s',
        timestamp,
        request.remote_addr,
        request.method,
        request.full_path,
        request.cookies,
        request.data,
        response.status,
        response.data
    )
    return response


@app.errorhandler(404)
def page_not_found(error):
    url = flask.request.path
    return """
          <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
          <title>404 Not Found</title>
          <h1>Not Found</h1>
          <p>The requested path <b>%s</b> was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>
          """ % url


@app.route('/send_host')
def set_target():
    return """
            <html>
                <title>Target selection</title>
                <body>
                    <form action="/scan">
                        Enter target IP: <input name="ip" type="text" />
                        <input name="submit" type="submit">
                    </form>
                </body>
            </html>
"""
def ip_val(ip: str):
    try:
        ip = ip.split(".")
        if len(ip) != 4:
            raise ValueError
        for i in ip:
            i = int(i)
            if i < 0 or i > 255:
                raise ValueError
        return ".".join(ip)
    except (TypeError, ValueError):
        return ""

import os


@app.route('/scan')
def scanner():
    ip = flask.request.args.get('ip')
    ip = ip_val(ip)
    if not ip:
        return "error address"
    result = os.popen('nmap ' + ip).read()
    return "%s" % result


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    app.run()

