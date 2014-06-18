from communications import app
from communications.communications import clean_data
from communications.communications import sendEmail
from communications.communications import validate_data
from flask import request
from werkzeug.wrappers import Response

@app.route("/email", methods=['POST'])
def send_mail():
  cleaned_data = clean_data(request.form)
  v_data = validate_data(cleaned_data)
  sendemail = sendEmail()
  response = sendemail.send(v_data)
  return Response(response)