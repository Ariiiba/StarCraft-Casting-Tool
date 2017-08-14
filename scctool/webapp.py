#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.webapp')

try:
    import requests, json
    import scctool.settings
    import webbrowser
    import requests.auth
    import urllib
    from PyQt5 import QtCore
    from flask import Flask, abort, request, current_app #pip install flask
    from uuid import uuid4
   
    NIGHTBOT_CLIENT_ID = "c120a9ad42370cf55bc1a609f1ca34ca" # Fill this in with your client ID
    NIGHTBOT_REDIRECT_URI = "http://localhost:65010/nightbot_callback"
    
    TWITCH_CLIENT_ID = "duam4gx9aryd46ub6qcdjrcxoghyak"
    TWITCH_REDIRECT_URI = "http://localhost:65010/twitch_callback"
    

except Exception as e:
    module_logger.exception("message") 
    raise  
    
def base_headers():
    return {"User-Agent": ""}
   
flask_app = Flask(__name__)   
   
@flask_app.route('/nightbot')
def home_nightbot():
    text = '''<script type="text/javascript">
                window.location = "%s";
                </script>'''
    return text % make_authorization_url_nightbot()

@flask_app.route('/twitch')
def home_twitch():
    text = '''<script type="text/javascript">
                window.location = "%s";
                </script>'''
    return text % make_authorization_url_twitch()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True
    
def make_authorization_url_nightbot():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": NIGHTBOT_CLIENT_ID,
              "response_type": "token",
              "state": state,
              "redirect_uri": NIGHTBOT_REDIRECT_URI,
              "scope": "commands"}
    url = "https://api.nightbot.tv/oauth2/authorize?" + urllib.parse.urlencode(params)
    return url
    
def make_authorization_url_twitch():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": TWITCH_CLIENT_ID,
              "response_type": "token",
              "state": state,
              "redirect_uri": TWITCH_REDIRECT_URI,
              "scope": "channel_editor"}
    url = "https://api.twitch.tv/kraken/oauth2/authorize?" + urllib.parse.urlencode(params)
    return url    

@flask_app.route('/nightbot_callback', methods=['GET'])
def nightbot_response_code():
    return '''  <script type="text/javascript">
                var token = window.location.href.split("#")[1]; 
                window.location = "/nightbot_callback_token?" + token;
            </script> '''
            
@flask_app.route('/twitch_callback', methods=['GET'])
def twitch_response_code():
    return '''  <script type="text/javascript">
                var token = window.location.href.split("#")[1]; 
                window.location = "/twitch_callback_token?" + token;
            </script> '''


@flask_app.route('/nightbot_callback_token')
def nightbot_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    access_token = request.args.get('access_token')
    
    w = FlaskThread._single
    w.token_nightbot = str(access_token)
    w.signal_nightbot.emit()
    shutdown_server()
    
    return  '''scctool: Succesfully recived access to Nightbot - you can close this tab now.'''
    
@flask_app.route('/twitch_callback_token')
def twitch_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    access_token = request.args.get('access_token')
    
    w = FlaskThread._single
    w.token_twitch = str(access_token)
    w.signal_twitch.emit()
    shutdown_server()
    
    return  '''scctool: Succesfully recived access to Twitch - you can close this tab now.'''
   
class FlaskThread(QtCore.QThread):
    signal_twitch = QtCore.pyqtSignal()
    signal_nightbot = QtCore.pyqtSignal()
    _single = None
    token_twitch = ""
    token_nightbot = ""
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        if FlaskThread._single:
            raise FlaskThread._single
        FlaskThread._single = self
        self.application = flask_app

    def __del__(self):
        self.wait()

    def run(self):
        module_logger.info("WebApp started")  
        self.application.run(port=65010)
        module_logger.info("WebApp done") 