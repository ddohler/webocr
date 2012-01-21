from django import forms

# Document upload form
class DocumentForm(forms.Form):
    upload_file = forms.FileField()
