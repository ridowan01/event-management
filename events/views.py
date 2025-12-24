from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import Event, Category, Participant
from .forms import CategoryMForm, EventMForm, ParticipantMForm

def index(request):
    curr_date = timezone.now()
    
    counts = Event.objects.aggregate(
        total=Count('id'),
        upcoming=Count('id', filter=Q(date__gte=curr_date)),
        past=Count('id', filter=Q(date__lt=curr_date))
    )

    events = Event.objects.select_related("category").prefetch_related("participants")

    category_type = request.GET.get("category")
    filter_type = request.GET.get("type") # Avoid using 'type' as it's a Python keyword

    if category_type and category_type != "all":
        events = events.filter(category__name=category_type)
    
    if filter_type == "upcoming":
        events = events.filter(date__gte=curr_date)
    elif filter_type == "past":
        events = events.filter(date__lt=curr_date)

    context = {
        "events": events,
        "participant_count": Participant.objects.count(),
        "categorys": Category.objects.all(),
        "upcoming_count": counts['upcoming'],
        "past_count": counts['past'],
    }
    return render(request, "events/index.html", context)


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