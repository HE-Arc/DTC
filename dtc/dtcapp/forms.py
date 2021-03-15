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
        fields = ['username','email','picture','password','id_twitch','pictureURL']
    username = forms.CharField(max_length=100,required=True)
    email = forms.CharField(max_length=100,required=True)
    picture = forms.ImageField(widget=PictureWidget)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password=forms.CharField(widget=forms.PasswordInput)
    id_twitch = forms.CharField(max_length=30,widget = forms.HiddenInput())
    pictureURL = forms.CharField(max_length=250,widget = forms.HiddenInput())

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

