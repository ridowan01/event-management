from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Category
from .forms import CategoryMForm, EventMForm

def home(request):
    return render(request, "events/home.html")

@login_required
def index(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()
    or request.user.groups.filter(name="Participant").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")
    
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
        "participant_count": User.objects.filter(attanded_events__isnull=False).count(),
        "categorys": Category.objects.all(),
        "upcoming_count": counts['upcoming'],
        "past_count": counts['past'],
        "query": query,
        "search_by": search_by,
    }
    return render(request, "events/index.html", context)

@login_required
def eventCreate(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")

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

@login_required
def eventEdit(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")

    event = get_object_or_404(Event, id=id)
    form = EventMForm(instance=event)

    if request.method == "POST":
        form = EventMForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
    
    return redirect("event-create")

@login_required
def eventDelete(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")

    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        event.delete()
    
    return redirect("event-create")

@login_required
def categoryCreate(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")

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

@login_required
def categoryEdit(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")

    category = get_object_or_404(Category, id=id)
    form = CategoryMForm(instance=category)

    if request.method == "POST":
        form = CategoryMForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
    
    return redirect("category-create")

@login_required
def categoryDelete(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Organizer").exists()):
        messages.error(request, "You do not have permission to access this page")
        return redirect("login")
        
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.delete()
    
    return redirect("category-create")
