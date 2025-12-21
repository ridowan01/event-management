from django import forms
from .models import Category, Event, Participant

class CategoryMForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

class EventMForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category"]

class ParticipantMForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["name", "email", "events"]