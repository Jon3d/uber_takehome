import nose
import unittest

from communications.communications import validate_data
from communications.communications import clean_data
from communications.communications import validate_email
from communications.communications import sendEmail
from communications.communications import Providers
from communications.communications import app
from unittest import mock
from werkzeug.exceptions import BadRequest

class SendEmailTestCases(unittest.TestCase):
  def setUp(self):
    self.send_email_obj = sendEmail()

  def tearDown(self):
    del self.send_email_obj

  def test_init(self):
    '''
    test verify init to default to sendmail provider venv var
    '''
    assert(self.send_email_obj.provider is \
           Providers(app.config['DEFAULT_SENDMAIL_PROVIDER']))

  def test_send_failure_mailgun_400(self):
    '''
    test that 400 response from mailgun returns to view
    '''
    mock_response = mock.Mock()
    mock_response.status_code = 400
    with mock.patch.object(sendEmail, 
                           'send_with_mailgun', 
                           return_value=mock_response) as mock_send:
      response = self.send_email_obj.send(None)
      self.send_email_obj.provider = Providers(1)
      assert response.status_code == 400

  def test_send_failure_maindrill_400(self):
    '''
    test that 400 response from mandrill returns to view
    '''
    mock_response = mock.Mock()
    mock_response.status_code = 400
    with mock.patch.object(sendEmail, 
                           'send_with_mandrill', 
                           return_value=mock_response) as mock_send:
      self.send_email_obj.provider = Providers(2)
      response = self.send_email_obj.send(None)
      assert response.status_code == 400

  def test_send_500_error_with_mailgun_retries_send_with_mandrill(self):
    '''
    Test on 500 error responses, each object is called just one time
    '''
    mock_response = mock.Mock()
    mock_response.status_code = 500
    with mock.patch.object(sendEmail, 
                           'send_with_mailgun', 
                           return_value=mock_response) as mock_mailgun:
      with mock.patch.object(sendEmail, 
                             'send_with_mandrill', 
                             return_value=mock_response) as mock_mandrill:
        self.send_email_obj.provider = Providers(1)
        response = self.send_email_obj.send(None)
        assert response.status_code == 500
        assert mock_mailgun.call_count == 1, (mock_mailgun.call_count, 1)
        assert mock_mandrill.call_count == 1, (mock_mandrill.call_count, 1)

  def test_send_500_error_with_mandrill_retries_send_with_mailgun(self):
    '''
    Test on 500 error responses, each object is called just one time
    '''
    mock_response = mock.Mock()
    mock_response.status_code = 500
    with mock.patch.object(sendEmail, 
                           'send_with_mailgun', 
                           return_value=mock_response) as mock_mailgun:
      with mock.patch.object(sendEmail, 
                             'send_with_mandrill', 
                             return_value=mock_response) as mock_mandrill:
        self.send_email_obj.provider = Providers(2)
        response = self.send_email_obj.send(None)
        assert response.status_code == 500
        assert mock_mailgun.call_count == 1, (mock_mailgun.call_count, 1)
        assert mock_mandrill.call_count == 1, (mock_mandrill.call_count, 1)


class CommunicationsTestCases(unittest.TestCase):
  def test_clean_data_empty_request_params(self):
    '''
    Test not including a payload
    '''
    params = None
    expected = None
    result = clean_data(None)
    self.assertEqual(expected, result), (expected, result)

  def test_clean_data_html_strip_from_body(self):
    '''
    Test html is stripped
    '''
    withHtml = dict(body='<head>test</head>')
    expected = dict(body='test')
    result = clean_data(withHtml)
    self.assertEqual(expected, result), (expected, result)

  def test_clean_data_doesnt_strip_from_key_value_that_is_not_body(self):
    '''
    Test html is not stripped from other key, values
    '''
    withHtml = dict(to_clean='<head>test</head>')
    expected = dict(to_clean='<head>test</head>')
    result = clean_data(withHtml)
    self.assertEqual(expected, result), (expected, result)

  def test_clean_data_whitespace_strip(self):
    '''
    Test whitespace is stripped
    '''
    withWhiteSpace = dict(to_clean='   test   ')
    expected = dict(to_clean='test')
    result = clean_data(withWhiteSpace)
    self.assertEqual(expected, result), (expected, result)

  def test_clean_data_newline_strip(self):
    '''
    Test new line characters are stripped
    '''
    withNewLine = dict(to_clean='test\n')
    expected = dict(to_clean='test')
    result = clean_data(withNewLine)
    self.assertEqual(expected, result), (expected, result)

  def test_validate_empty_request_params(self):
    '''
    Test validate empty not including a payload
    '''
    nose.tools.assert_raises(BadRequest, validate_data, None)

  def test_validate_email_correct(self):
    '''
    Test valid email address passes valid_email()
    '''
    correctEmail = 'test@test.test'
    response = validate_email(correctEmail)
    self.assertEqual(True, response)

  def test_validate_email_no_at(self):
    '''
    Test email address with no @ fails valid_email()
    '''
    incorrectEmail = 'testtest.test'
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_email_no_username(self):
    '''
    Test email address with no username fails valid_email()
    '''
    incorrectEmail = '@test.test'
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_email_no_hostname(self):
    '''
    Test email address with no hostname fails valid_email()
    '''
    incorrectEmail = 'test@'
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_email_partial_hostname(self):
    '''
    Test email address with partial hostname fails  valid_email
    '''
    incorrectEmail = 'test@test.'
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_email_partial_hostname_end(self):
    '''
    Test email address with partial hostname fails  valid_email
    '''
    incorrectEmail = 'test@.test'
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_no_email(self):
    '''
    Test empty fails valid_email
    '''
    incorrectEmail = ''
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_nonetype_email(self):
    '''
    Test empty fails valid_email
    '''
    incorrectEmail = None
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)

  def test_validate_wrong_type_email(self):
    '''
    Test wrong type fails valid_email
    '''
    incorrectEmail = 0
    response = validate_email(incorrectEmail)
    self.assertEqual(False, response)