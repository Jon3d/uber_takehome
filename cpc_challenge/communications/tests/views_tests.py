import mock
import nose
import unittest
from communications import app 
from werkzeug.exceptions import BadRequest


class ViewsTestCases(unittest.TestCase):
  def setUp(self):
    self.endpoint = "/email"
    self.app = app.test_client()
    self.request_data = {'to':'fake@example.com',
                         'to_name':'Ms. Fake',
                         'from':'noreply@uber.com',
                         'from_name':'Uber',
                         'subject':'A Message from Uber',
                         'body':'<h1>Your Bill</h1><p>$10</p>'}

  def tearDown(self):
    self.app.data = {}
    self.app.free_id = 0

  def test_get(self):
    '''
    Test GET returns 405, method not allowed
    '''
    response = self.app.get(self.endpoint)
    self.assertEqual(response.status_code, 405)

  def test_missing_required_fields(self):
    '''
    Test if a required field is missing, 400 is recieved
    '''
    for x in self.request_data:
      incomplete_params = self.request_data.copy()
      del incomplete_params[x]
      response = self.app.post(self.endpoint, data=incomplete_params)
      self.assertEqual(response.status_code, 400)

  def test_incomplete_required_fields(self):
    '''
    Test if a required field is empty, 400 is recieved
    '''
    for x in self.request_data:
      incomplete_params = self.request_data.copy()
      incomplete_params[x] = None
      response = self.app.post(self.endpoint, data=incomplete_params)
      self.assertEqual(response.status_code, 400)

  def test_no_arguments(self):
    '''
    Test no arguments returns 400
    '''
    response = self.app.post(self.endpoint, data=None)
    self.assertEqual(response.status_code, 400)
