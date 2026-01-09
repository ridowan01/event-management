from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import Event, Category, Participant
from .forms import CategoryMForm, EventMForm, ParticipantMForm

def index(request):
    curr_date = timezone.now().date()
    
    counts = Event.objects.aggregate(
        total=Count('id'),
        upcoming=Count('id', filter=Q(date__gte=curr_date)),
        past=Count('id', filter=Q(date__lt=curr_date))
    )

    events = Event.objects.select_related("category").prefetch_related("participants")

    query = request.GET.get("q")
    search_by = request.GET.get("by")
    
    if query:
        if search_by == "category":
            events = events.filter(category__name__icontains=query)
        elif search_by == "location":
            events = events.filter(location__icontains=query)
        else:
            events = events.filter(name__icontains=query)

    category_type = request.GET.get("category")
    filter_type = request.GET.get("type") 

    if category_type and category_type != "all":
        events = events.filter(category__name=category_type)
        
    if filter_type == "upcoming":
        events = events.filter(date__gte=curr_date)
    elif filter_type == "past":
        events = events.filter(date__lt=curr_date)
    elif not filter_type and not query:
        events = events.filter(date=curr_date)

    context = {
        "events": events,
        "participant_count": Participant.objects.count(),
        "categorys": Category.objects.all(),
        "upcoming_count": counts['upcoming'],
        "past_count": counts['past'],
        "query": query,
        "search_by": search_by,
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
        "active_tab": "event",
        "form": form,
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

    context = {
        "categorys": categorys,
        "active_tab": "category",
        "form": form,
    }
    return render(request, "events/category.html", context)

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
        "active_tab": "participant",
        "form": form,
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