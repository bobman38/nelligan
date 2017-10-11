from django import forms
from .models import Family
from django.utils.html import escape

def add_class_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels."""
    def required_tag(self, contents=None, attrs=None, label_suffix=None):
        contents = contents or escape(self)
        attrs = {'class': 'input'}
        return original_function(self, contents, attrs, label_suffix)
    return required_tag

def decorate_bound_field():
  from django.forms.forms import BoundField
  BoundField.field = add_class_tag(BoundField.field)

decorate_bound_field()
