from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Category
from .forms import CategoryMForm, EventMForm

def is_organizer(user):
    if user.is_authenticated:
        return user.groups.filter(name="Organizer").exists()
    return False

# Create your views here.

def home(request):
    return render(request, "events/home.html")

@login_required
def index(request):
    if not (request.user.is_superuser or is_organizer(request.user)
    or request.user.groups.filter(name="Participant").exists()):
        messages.error(request, "You do not have permission to access this page, Login first")
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
    elif filter_type == "participated":
        events = events.filter(participants=request.user)
    elif not filter_type and not query:
        events = events.filter(date=curr_date)

    context = {
        "events": events,
        "categorys": Category.objects.all(),
        "total_count": counts['total'],
        "upcoming_count": counts['upcoming'],
        "past_count": counts['past'],
        "query": query,
        "search_by": search_by,
    }
    return render(request, "events/index.html", context)

@login_required
def partipateEvent(request, id):
    if not (request.user.is_superuser or is_organizer(request.user)
    or request.user.groups.filter(name="Participant").exists()):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")
    
    event = get_object_or_404(Event, id=id)
    if request.method == "POST":
        if request.user in event.participants.all():
            messages.warning(request, "You have already participated in this event")
        else:
            event.participants.add(request.user)
            messages.success(request, "You have successfully participated in this event")

            # sending mail
            subject = f"You have successfully participated in {event.name}"
            message = f"Hi {request.user.username},\n\nYou have successfully participated in {event.name} on {event.date} at {event.time} in {event.location}.\nWe look forward to see you there.\n\nBest Regards,\nThe Event.io Team"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]

            # if has email
            if request.user.email:
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    messages.success(request, "Participation successfull")
                except:
                    messages.warning(request, "Email sending failed")
            else:
                messages.warning(request, "Your account don't have email")

    return redirect("index")

@login_required
def cancelPartipateEvent(request, id):
    if not (request.user.is_superuser or is_organizer(request.user)
    or request.user.groups.filter(name="Participant").exists()):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")
    
    event = get_object_or_404(Event, id=id)
    if request.method == "POST":
        if request.user in event.participants.all():
            event.participants.remove(request.user)
            messages.success(request, "You have successfully canceled your participation in this event")

            # sending email
            subject = f"Cancelation of participation in {event.name}"
            message = f"Hi {request.user.username},\n\nYou have successfully canceled your participation in {event.name} on {event.date} at {event.time} in {event.location}.\n\nBest Regards,\nThe Event.io Team"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.warning(request, "Event Participation Cancelled")
            except:
                messages.warning(request, "Email sending failed")
        else:
            messages.warning(request, "You have not participated in this event")
    return redirect("index")


@login_required
def eventCreate(request):
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")

    events = Event.objects.prefetch_related("participants")
    categorys = Category.objects.all()
    form = EventMForm()

    if request.method == "POST":
        form = EventMForm(request.POST, request.FILES)
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
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")

    event = get_object_or_404(Event, id=id)
    form = EventMForm(instance=event)

    if request.method == "POST":
        form = EventMForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
    
    return redirect("event-create")

@login_required
def eventDelete(request, id):
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")

    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        event.delete()
    
    return redirect("event-create")

@login_required
def categoryCreate(request):
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
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
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
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
    if not (request.user.is_superuser or is_organizer(request.user)):
        messages.error(request, "You do not have permission to access this page, Login first")
        return redirect("login")
        
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.delete()
    
    return redirect("category-create")

@login_required
def participantList(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to access this page")
    
    users = User.objects.all()
    groups = Group.objects.all()

    users_with_groups = []
    for user in users:
        user.current_group = user.groups.first()
        users_with_groups.append(user)

    context = {
        "users": users_with_groups,
        "active_tab": "participant",
        "groups": groups,
    }

    return render(request, "events/participant.html", context)


@login_required
def participantRoleEdit(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to access this page")
    
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        group_id = request.POST.get("role")

        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)

        user.groups.clear()
        user.groups.add(group)

    return redirect("participant-list")

@login_required
def participantDelete(request, id):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to access this page")
    
    if request.method == "POST":
        if request.user.id == id:
            messages.warning(request, "You cannot delete yourself")
        else:
            user = User.objects.get(id=id)
            user.delete()

    return redirect("participant-list")