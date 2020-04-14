from flask import Flask, request
from threading import Lock
import os
import socket
import subprocess
import time
import random
import uuid


app = Flask(__name__)
lock = Lock()
visits = 0

def getIPInfo():
    process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    lastKey = ''
    dat = {}
    for line in out.split(b'\n'):
        vals = line.split()
        if len(vals) == 0:
            continue
        if vals[1] == b'Link' or vals[1].startswith(b'flags'):
            latestKey = vals[0]
        if vals[0] == b'inet':
            splitVal = vals[1].split(b':')
            if len(splitVal) > 1:
                dat[latestKey] = vals[1].split(b':')[1]
            else:
                dat[latestKey] = vals[1]
    return dat
def format(d):
    out = ''
    for key in d.keys():
        out += '{:<16}{}\n'.format(key.decode('utf-8'), d[key].decode('utf-8'))
    return out
        
        
ipInfo = format(getIPInfo())

HTML_TEMPLATE = '''\
<html>
    <head>
        <style>
            body {{
                background-color: {color}
            }}
        </style>
    </head>
    <body>
        <h1>Service: {service}</h1>
        <h2>Path: {path}</h2>
        <b>Hostname:</b> {hostname}<br/>
        <b>Visits:</b> {visits}<br/>
        <b>Remote IP:</b> {remoteIp}<br/>
        <b>Request's Host:</b> {requestHost}<br/><br/>
        <b>Local IP Info</b>
        <pre>{ip}</pre>
    </body>
</html>
'''

def color(number):
    return "#" + hex(number % (255*255*255))[2:]


def getVals(path):
    mac = uuid.getnode()
    global visits, ip
    with lock:
        visits += 1
    return {'color':color(mac), 'service':str(mac), 'path':path, 
        'hostname':socket.gethostname(), 
        'visits':visits, 'remoteIp':request.remote_addr, 
        'requestHost':request.environ.get('HTTP_HOST',''), 'ip':ipInfo}
    
@app.route("/")
def root():
    return HTML_TEMPLATE.format(**getVals("root"))

@app.route("/a")
def a():
    return HTML_TEMPLATE.format(**getVals("a"))

@app.route("/b")
def b():
    return HTML_TEMPLATE.format(**getVals("b"))
    
@app.route("/c")
def c():
    return HTML_TEMPLATE.format(**getVals("c"))
    
@app.route("/d")
def d():
    return HTML_TEMPLATE.format(**getVals("d"))
    
@app.route("/e")
def e():
    return HTML_TEMPLATE.format(**getVals("e"))

@app.route("/pause/<int:pauseTime>")
def pause(pauseTime):
    time.sleep(pauseTime)
    return HTML_TEMPLATE.format(**getVals("pause"))

@app.route("/randpause/<int:pauseTime>")
def randpause(pauseTime):
    time.sleep(random.randint(1,pauseTime))
    return HTML_TEMPLATE.format(**getVals("randpause"))


if __name__ == "__main__":
    app.run(host='::', port=5555)
    print("stopped running")

