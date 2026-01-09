from django import forms
from .models import Category, Event

class CategoryMForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

class EventMForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category"]