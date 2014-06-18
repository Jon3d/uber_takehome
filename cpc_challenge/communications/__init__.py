from flask import Flask
app = Flask(__name__)

app.config.from_object('communications.default_settings')
app.config.from_envvar('COMMUNICATIONS_SETTINGS')

import communications.views