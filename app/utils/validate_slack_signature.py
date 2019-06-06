import datetime
import hashlib
import hmac

def validate_slack_signature(func):
    """
    Cryptographically validates that the incoming message came from Slack, using the
    Slack 'signing secret'
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Retrieve the X-Slack-Request-Timestamp header on the HTTP request
        timestamp = request.headers.get("X-Slack-Request-Timestamp")

        if absolute_value(datetime.datetime.now() - timestamp) > 60 * 5: 
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
