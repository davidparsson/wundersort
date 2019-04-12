import os
import pathlib

from flask import Flask, redirect, request, session, url_for
from flask.json import jsonify
from requests_oauthlib import OAuth2Session

app = Flask(__name__)

client_id = pathlib.Path('.client_id').read_text().strip()
client_secret = pathlib.Path('.client_secret').read_text().strip()

authorization_base_url = 'https://www.wunderlist.com/oauth/authorize'
token_url = 'https://www.wunderlist.com/oauth/access_token'

token_file = pathlib.Path('.access_token')

@app.route("/")
def index():
    return redirect(url_for('.login'))

@app.route("/login")
def login():
    wunderlist = OAuth2Session(client_id, redirect_uri='http://localhost:5000/callback')  # TODO(dp): Resolve full uri?
    authorization_url, state = wunderlist.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    wunderlist = OAuth2Session(client_id, state=session['oauth_state'])
    token = wunderlist.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)

    with token_file.open('w') as open_file:
        open_file.write(token['access_token'])
    return redirect(url_for('.shutdown'))

@app.route("/shutdown")
def shutdown():
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    shutdown_server()
    return "Done!"

def get_access_token():
    if not token_file.is_file():
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

        app.secret_key = os.urandom(24)
        app.run(debug=True)
    return token_file.read_text().strip()


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
