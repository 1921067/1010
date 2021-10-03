from django import forms
from django.db import models
from django.forms import fields
from.models import Message,Group,Friend,Good
from django.contrib.auth.models import User

#message
class MessageForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ['owner', 'group', 'content']

#group
class GroupForm(forms.ModelForm):
  class Meta:
    model = Group
    fields = ['owner', 'title'] 


#friend
class FriendForm(forms.ModelForm):
  class Meta:
    model = Friend
    fields = ['owner', 'user', 'group'] 


#Good
class GoodForm(forms.ModelForm):
  class Meta:
    model = Good
    fields = ['owner', 'message'] 


#group checkbox
class GroupCheckForm(forms.Form):
  def __init__(self, user, *args, **kwargs):
    super(GroupCheckForm, self).__init__(*args, **kwargs)
    public = User.objects.filter(username='public').first()
    self.fields['groups'] = forms.MultipleChoiceField(
      choices=[(item.title, item.title) for item in \
        Group.objects.filter(owner__in=[user,public])],
      widget=forms.CheckboxSelectMultiple(),
    )



#group menu
class GroupSelectForm(forms.Form):
  def __init__(self, user, *args, **kwargs):
    super(GroupSelectForm, self).__init__(*args, **kwargs)
    self.fields['groups'] = forms.ChoiceField(
      choices=[('-','-')] + [(item.title, item.title) \
      for item in Group.objects.filter(owner=user)],
      widget=forms.Select(attrs={'class':'form-control'}),
    )



#Friend check
class FriendsForm(forms.Form):
  def __init__(self, user, friends=[], vals=[], *args, **kwargs):
    super(FriendsForm, self).__init__(*args, **kwargs)
    self.fields['friends'] = forms.MultipleChoiceField(
      choices=[(item.user, item.user) for item in friends],
      widget=forms.CheckboxSelectMultiple(),
      initial=vals
    )



#Friend check
class CreateGroupForm(forms.Form):
  group_name = forms.CharField(max_length=50, \
    widget=forms.TextInput(attrs={'class':'form-control'}),
  ) 



#toukou
class PostForm(forms.Form):
  content = forms.CharField(max_length=500, \
    widget= forms.Textarea(attrs={'class':'form-control', 'rows':2}),
  ) 

  def __init__(self, user, *args, **kwargs):
    super(PostForm, self).__init__(*args, **kwargs)
    public = User.objects.filter(username='public').first()
    self.fields['groups'] = forms.ChoiceField(
      choices=[('-','-')] + [(item.title, item.title) \
        for item in Group.objects. \
        filter(owner__in=[user,public])],  
        widget=forms.Select(attrs={'class':'form-control'}),
    )
