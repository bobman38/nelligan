from django import forms
from .models import *
from .services import *

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['label', 'code', 'pin']

    def clean(self):
        cleaned_data = super(CardForm, self).clean()
        code = cleaned_data.get("code")
        pin = cleaned_data.get("pin")

        if not check_card(code, pin):
            msg = "Can't logon on Nelligan"
            self.add_error('code', msg)
            self.add_error('pin', msg)

class BookSearchForm(forms.Form):
    search = forms.CharField()

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['card', 'name', 'library']
    name = forms.CharField(disabled=True, label='Nom', required=False)



