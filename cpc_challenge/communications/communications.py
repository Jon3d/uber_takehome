from enum import Enum
from flask import abort
from jinja2.filters import do_striptags
import json
import re
import requests

from communications import app

class Providers(Enum):
  MAILGUN = 1
  MANDRILL = 2

class sendEmail:
  def __init__(self):
    self.retried = False
    try:
      self.provider = Providers(app.config['DEFAULT_SENDMAIL_PROVIDER'])
    except KeyError:
      self.provider = Providers(1)
      print("ERROR, env var for SENDMAIL_PROVIDER not found")

  def send(self, data):
    '''
    Send mail via default provider, if message fails with a server
    Error, try the other provider, if both fail respond with failure 
    message
    '''
    response = self.send_with_mailgun(data) \
               if self.provider is Providers.MAILGUN \
               else self.send_with_mandrill(data)

    if self.retried is False and str(response.status_code)[0] is '5':
      print("%s sendmail recieved server error %s", \
            self.provider, response.status_code)

      self.provider = Providers.MANDRILL if \
                      self.provider is Providers.MAILGUN \
                      else Providers.MAILGUN

      self.retried = True
      self.send(data)
    elif str(response.status_code)[0] is '4':
      print("%s sendmail failed with error %s ", \
            self.provider, response.status_code)

    self.retried = False
    return response

  def send_with_mailgun(self, data):
    '''
    send email with mailgun
    '''
    from_val = "{0!s} <{1!s}>".format( data['from_name'], data['from'])
    to_val = "{0!s} <{1!s}>".format( data['to_name'], data['to'])

    sendmail_data={"from": from_val,
                   "to": to_val,
                   "subject": data['subject'],
                   "text": data['body']}

    return requests.post(app.config['MAILGUN_SENDMAIL_ADDRESS'],
                         auth=("api", app.config['MAILGUN_AUTH_KEY']),
                         data=sendmail_data)

  def send_with_mandrill(self, data):
    '''
    send email with mandrill
    '''
    message = {"from_email": data['from'],
               "from_name": data['from_name'],
               "subject": data['subject'],
               "text": data['body'],
               "to": [{'email': data['to'],
                       "name": data['to_name'],
                       "type": "to"}],
               "track_clicks": None, 
               "track_opens": None}

    data = dict(key=app.config['MANDRILL_AUTH_KEY'],
                message=message,
                async=False,
                ip_pool=None,
                send_at=None)
    
    data = json.dumps(data)

    return requests.post(url=app.config['MANDRILL_SENDMAIL_ADDRESS'],
                         data=data,
                         headers={'content-type':'application/json'})

def validate_email(email):
  '''
  Very basic email validation
  '''  
  return type(email) is str and \
         re.match(r".+@.+\..+", email) is not None

def clean_data(params):
  ''' 
  Strips whitespace from data, and html tags from body if in params
  '''
  if params is None: return None
  cleaned_data = {}
  for x in params:
    cleaned = params[x]
    cleaned = cleaned.strip()
    cleaned_data[x] = cleaned

  if 'body' in cleaned_data.keys():
    cleaned_data['body'] = do_striptags(cleaned_data['body'])
  return cleaned_data

def validate_data(params):
  '''
  Validate all required fields are present and valid
  '''
  if params is None: abort(400, 'Missing required fields')

  required_data = ['to', 'to_name', 'from', 'from_name', 'subject', 'body']
  for x in required_data:
    if x not in params or params[x] == None: 
      abort(400, 'Missing required fields')

  if not validate_email(params['from']) or not validate_email(params['to']):
    abort(400, 'Invalid Email')

  return params