from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Category, Participant
from .forms import CategoryMForm, EventMForm, ParticipantMForm
from django.utils import timezone

# Create your views here.
def index(request):
    events = Event.objects.prefetch_related("participants")
    participant_count = Participant.objects.all().count()
    categorys = Category.objects.all()

    curr_date = timezone.now()
    upcoming_events = events.filter(date__gte=curr_date).count()
    past_events = events.filter(date__lt=curr_date).count()

    context = {
        "events": events,
        "participant_count": participant_count,
        "categorys": categorys,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }
    return render(request, "events/index.html", context=context)

def eventCreate(request):
    events = Event.objects.prefetch_related("participants")
    categorys = Category.objects.all()
    form = EventMForm()

    if request.method == "POST":
        form = EventMForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("event-create")
    
    context = {
        "events": events,
        "categorys": categorys,
    }
    return render(request, "events/event.html", context=context)

def eventEdit(request, id):
    event = get_object_or_404(Event, id=id)
    form = EventMForm(instance=event)

    if request.method == "POST":
        form = EventMForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
    
    return redirect("event-create")

def eventDelete(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        event.delete()
    
    return redirect("event-create")

def categoryCreate(request):
    categorys = Category.objects.all()
    form = CategoryMForm()

    if request.method == "POST":
        form = CategoryMForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("category-create")

    return render(request, "events/category.html", {"categorys": categorys})

def categoryEdit(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryMForm(instance=category)

    if request.method == "POST":
        form = CategoryMForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
    
    return redirect("category-create")

def categoryDelete(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.delete()
    
    return redirect("category-create")

def participantCreate(request):
    participants = Participant.objects.all()
    events = Event.objects.all()
    form = ParticipantMForm()

    if request.method == "POST":
        form = ParticipantMForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("participant-create")

    context = {
        "participants": participants,
        "events": events,
    }
    return render(request, "events/participant.html", context=context)

def participantEdit(request, id):
    participant = get_object_or_404(Participant, id=id)
    form = ParticipantMForm(instance=participant)

    if request.method == "POST":
        form = ParticipantMForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
    
    return redirect("participant-create")

def participantDelete(request, id):
    participant = get_object_or_404(Participant, id=id)

    if request.method == "POST":
        participant.delete()
    
    return redirect("participant-create")