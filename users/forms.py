from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from review.models import Dorm, Room
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@wheatoncollege.edu'):
            raise ValidationError("Email must end with @wheatoncollege.edu")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    dorm = forms.ModelChoiceField(
        queryset=Dorm.objects.all().order_by('name'),
        required=False,
        empty_label="Select a dorm first",
        help_text="Select your dorm building"
    )

    class Meta:
        model = Profile
        fields = ['image', 'assigned_room']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        # Set initial queryset to all rooms (to avoid validation errors)
        self.fields['assigned_room'].queryset = Room.objects.all()
        self.fields['assigned_room'].empty_label = "Select a room"
        self.fields['assigned_room'].label = "Assigned Room"
        self.fields['assigned_room'].help_text = "Select your dorm room. This is required to post reviews."

        # If instance (profile) has a room assigned, populate the fields
        if self.instance and self.instance.pk and self.instance.assigned_room:
            # Set the dorm field initial value
            self.fields['dorm'].initial = self.instance.assigned_room.dorm

        # Explicitly reorder fields to ensure dorm appears before room
        field_order = ['image', 'dorm', 'assigned_room']
        self.order_fields(field_order)