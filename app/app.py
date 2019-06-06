#!/usr/local/bin/python3
import os
import utils.validate_slack_signature
from flask import Flask, request
from redis import Redis

# This `app` represents your existing Flask app
app = Flask(__name__)
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint="/slack/events", app)

r = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], decode_responses=True)
bind_port = int(os.environ['BIND_PORT'])


def splitkey(userkey):
    """Splits a 'userkey' string at the first '~' character and returns that pair of strings"""
    mylist = userkey.split('~', 1)
    user_id, key = mylist[0], mylist[1]
    return (user_id, key)


def set(name=None, value=None):
    """Given a key name, set or delete that key in the redis datastore"""
    if name is None:
        return 'Error, need a key'
    elif value is None: # delete the key,value pair
        r.delete(name)
        user_id, key = splitkey(name)
        return f'{key} deleted.'
    else: # set (or overwrite) the key,value pair
        r.set(name, value)
        set_val = r.get(name)
        if set_val is None:
            return 'Error, value not set properly.'
        else:
            user_id, key = splitkey(name)
            return f'"{key}" set to "{set_val}"'


def get(name=None):
    """Given a key name, get that key's value from the redis datastore"""
    if name is None:
        return 'Error, no key entered'
    else: 
        # return all key,value pairs that start with given string
        mystr = ''
        for userkey in r.scan_iter(name+'*'):
            user_id, key = splitkey(userkey)
            mystr += key + '=' + r.get(userkey) + ', '
        if mystr is '':
            return f'no keys start with given string'
        else:
            return mystr


def handle(command):
    """Handle a command that has been passed from the Flask route. Either help, set, get, or delete."""
    if 'help' in command:
        return 'HELP. Usage (set, get, del): \n /remember key=value \n /remember key \n /remember key='
    else:
        if '=' in command: # pass to set
            mylist = command.split('=')
            name, value = mylist[0].strip(), mylist[1].strip()
            if value is '':
                return set(name) # delete
            else:
                return set(name,value) # set
        else: # pass to get
            return get(command)


@app.route('/remember', methods=['POST'])
@utils.validate_slack_signature
def remember():
    """Flask route for remmeber slash command. Prepend user_id~ to text entered and pass on to handler"""
    return handle(request.form['user_id'] + '~' + request.form['text'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=bind_port)
