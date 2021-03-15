from django import forms
from .models import User

from string import Template
from django.utils.safestring import mark_safe

class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, **kwargs):
        html =  Template("""<img src="$link"/>""")
        return mark_safe(html.substitute(link=value))

class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','picture','password']
    username = forms.CharField(max_length=100,required=True)
    email = forms.CharField(max_length=100,required=True)
    picture = forms.ImageField(widget=PictureWidget)
    password = forms.CharField(widget=forms.PasswordInput)
