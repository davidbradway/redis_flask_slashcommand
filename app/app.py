#!/usr/local/bin/python3
import os
from flask import Flask
from redis import Redis

app = Flask(__name__)
r = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])
bind_port = int(os.environ['BIND_PORT'])


@app.route('/set/<name>', strict_slashes=False)
@app.route('/set/<name>/<value>', strict_slashes=False)
def set(name=None, value=None):
    if name is None:
        return 'Error, need a name'
    elif value is None: # delete the key, value pair
        r.delete(name)
        return f'{name} deleted.'
    else: # set (or overwrite) the key, value pair
        r.set(name, value)
        set_val = r.get(name)
        if set_val is None:
            return 'Error, value not set properly.'
        else:
            return f'{name} set to {set_val.decode()}'


@app.route('/get', strict_slashes=False)
@app.route('/get/<name>', strict_slashes=False)
def get(name=None):
    if name is None: # return a list of all keys
        keylist = list()
        for key in r.scan_iter():
            keylist.append(key.decode())
        return 'All keys: ' + ', '.join(keylist)
    else: # return one key, value pair
        set_val = r.get(name)
        if set_val is None:
            return f'{name} did not exist'
        else:
            return f'{name}={set_val.decode()}'


@app.route('/remember_local', strict_slashes=False)
@app.route('/remember_local/<command>', strict_slashes=False)
def remember_local(command=None):
    if command is None: # return all keys
        return get(None)
    else:
        if '=' in command: # pass to set
            mylist = command.split('=')
            name, value = mylist[0].strip(), mylist[1].strip()
            if value is '':
                # delete
                return set(name)
            else:
                return set(name,value)
        else: # pass to get
            return get(command)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=bind_port)
