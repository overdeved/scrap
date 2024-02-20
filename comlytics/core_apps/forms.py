from django import forms

class QuerryForm(forms.Form):
    keyword = forms.CharField(label='Enter keyword:', max_length=120)
    pages = forms.IntegerField(label='How many pages?', max_value=10)
