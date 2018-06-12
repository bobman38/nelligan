from django.test import TestCase
from .services import *
# import re

# Create your tests here.
class CardTestCase(TestCase):
    # def setUp(self):

    def test_detect_duedate(self):
        """Check if duedate only is OK"""
        text = ' DUE 18-07-07'
        duedate, renewed, fine = duedate_book(text)
        self.assertEqual(duedate, '18-07-07')
        self.assertEqual(renewed, 0)

    def test_detect_fine(self):
        """Check if fine is OK"""
        text = ' DUE 18-06-10 FINE(up to now) 0.10$'
        duedate, renewed, fine = duedate_book(text)
        self.assertEqual(duedate, '18-06-10')
        self.assertEqual(fine, '0.10')
        self.assertEqual(renewed, 0)

    def test_detect_renew(self):
        """Check if renew is OK"""
        text = ' DUE 18-06-30  Renewed 1 time'
        duedate, renewed, fine = duedate_book(text)
        self.assertEqual(duedate, '18-06-30')
        self.assertEqual(renewed, 1)