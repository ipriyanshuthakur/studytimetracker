from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Record, UserSettings
from datetime import datetime, timedelta, time


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	


# user setting form
class UserSettingsForm(forms.ModelForm):
	daily_target_hours = forms.DecimalField(
		widget=forms.widgets.NumberInput(attrs={"placeholder": "Hours", "class": "form-control", "min": "0", "max": "18", "step": "0.5"}),
		label="",
		initial=8
	)
	max_queued = forms.IntegerField(
		widget=forms.widgets.NumberInput(attrs={"placeholder": "max_queued", "class": "form-control", "min": "0", "max": "10",}),
		label="",
		initial=5
	)
	target_goal = forms.CharField(
		widget=forms.TextInput(attrs={"placeholder": "Goal", "class": "form-control"}),
		label="",
		required=False
	)
	target_date = forms.DateField(
		widget=forms.DateInput(attrs={"placeholder": "Target Date", "class": "form-control", "type": "date"}),
		label="",
		required=False
	)
	thestart_date = forms.DateField(
		widget=forms.DateInput(attrs={"placeholder": "The Start Date", "class": "form-control", "type": "date"}),
		label="",
		required=False
	)
	class Meta:
		model = UserSettings
		fields = ['daily_target_hours', 'max_queued', 'target_goal', 'target_date', 'thestart_date'] 




class AddSubForm(forms.ModelForm):
    subname = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Subject", "class": "form-control"}),
        label=""
    )
    topic = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Topic", "class": "form-control"}),
        label=""
    )

    class Meta:
        model = Record
        exclude = ("user", "queue_no", "created_at","start_at", "done_at")


from django import forms
from datetime import datetime

class MySearchForm(forms.Form):
    date_range_start = forms.DateField( 
        required=False, 
        widget=forms.DateInput(attrs={'placeholder':'From:','class': 'form-control', 'type': 'date', 'max': datetime.now().date()})
    )
    date_range_end = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'placeholder':'To:', 'class': 'form-control', 'type': 'date', 'max': datetime.now().date()})
    )
    single_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'placeholder':'Enter a Date', 'class': 'form-control', 'type': 'date', 'max': datetime.now().date()}),
    	label='Enter a Date', 
    )
    findsubject = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={"placeholder": "Subject Name", "class": "form-control"}),
        label='Subject Name', 
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(MySearchForm, self).__init__(*args, **kwargs)
        # Set the max attribute for the DateInput fields to the current date
        self.fields['date_range_start'].widget.attrs['max'] = datetime.now().date()
        self.fields['date_range_end'].widget.attrs['max'] = datetime.now().date()
        self.fields['single_date'].widget.attrs['max'] = datetime.now().date()








