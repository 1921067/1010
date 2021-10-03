#from typing_extensions import Required
from django import forms
from django.db.models import fields
from django.forms import widgets
from.models import Friend
from hello import models
from.models import Friend, Message


class FriendForm(forms.ModelForm):
  class Meta:
    model = Friend
    fields = ['name', 'mail', 'gender', 'age', 'birthday']


class FindForm(forms.Form):
  find = forms.CharField(label='Find', required=False,\
    widget=forms.TextInput(attrs={'class':'form-control'}))


class CheckForm(forms.Form):
  str = forms.CharField(label='String',\
    widget=forms.TextInput(attrs={'class':'form-control'}))

  def clean(self):
    cleaned_data = super().clean()
    str = cleaned_data['str']
    if(str.lower().startswith('no')):
      raise forms.ValidationError('You input "NO"!')



class MessageForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ['title', 'content','friend']
    widgets = {
      'title': forms.TextInput(attrs={'class':'form-control form-control-sm'}),
      'content': forms.Textarea(attrs={'class':'form-control form-control-sm', 'rows':2}),
      'friend': forms.Select(attrs={'class':'form-control form-control-sm'}),
    }
