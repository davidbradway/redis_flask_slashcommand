#!/usr/local/bin/python3
import os
import datetime
import hashlib
import hmac
from flask import Flask, request
from redis import Redis
from slackeventsapi import SlackEventAdapter
from functools import wraps

# This `app` represents your existing Flask app
app = Flask(__name__)
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

r = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], decode_responses=True)
bind_port = int(os.environ['BIND_PORT'])


def validate_slack_signature(func):
    """
    Cryptographically validates that the incoming message came from Slack, using the
    Slack 'signing secret'
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Retrieve the X-Slack-Request-Timestamp header on the HTTP request
        timestamp = request.headers.get("X-Slack-Request-Timestamp")

        if abs(datetime.datetime.now() - timestamp) > 60 * 5: 
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            return "", http.HTTPStatus.NO_CONTENT

        # Retrieve the X-Slack-Signature header on the HTTP request, and the body of the request
        signature = request.headers.get("X-Slack-Signature")
        body = request.get_data(as_text=True)

        # Concatenate the version number (right now always v0), 
        #  the timestamp, and the body of the request.
        # Use a colon as the delimiter and encode as bytestring
        format_req = str.encode(f"v0:{timestamp}:{body}")

        # Encode as bytestring
        encoded_secret = str.encode(SLACK_SIGNING_SECRET)

        # Using HMAC SHA256, hash the above basestring, using the Slack Signing Secret as the key.
        request_hash = hmac.new(encoded_secret, format_req, hashlib.sha256).hexdigest()

        # Compare this computed signature to the X-Slack-Signature header on the request.
        if hmac.compare_digest(f"v0={request_hash}", signature):
            # hooray, the request came from Slack! Run the decorated function
            return func(*args, **kwargs)
        else:
            return "", http.HTTPStatus.NO_CONTENT

    return wrapper


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


@app.route('/remember', methods=['POST'])
@validate_slack_signature
def remember():
    """Flask route for remmeber slash command. Prepend user_id~ to text entered and pass on to handler"""
    text = request.form['text']

    """Handle a command with either help, set, get, or delete."""
    if 'help' in text:
        return 'HELP. Usage (set, get, del): \n /remember key=value \n /remember key \n /remember key='
    else:
        user_id = request.form['user_id']
        if '=' in text:
            mylist = text.split('=')
            name, value = mylist[0].strip(), mylist[1].strip()
            if value is '':
                return set(user_id + '~' + name) # delete
            else:
                return set(user_id + '~' + name,value) # set
        else:
            return get(user_id + '~' + text) # get
    return 


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=bind_port)
