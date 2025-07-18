from django import forms

class LogUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")
