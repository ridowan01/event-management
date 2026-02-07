from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, Category
from .forms import CategoryMForm, EventMForm

User = get_user_model()

def is_organizer(user):
    if user.is_authenticated:
        return user.groups.filter(name="Organizer").exists()
    return False

def is_participant(user):
    if user.is_authenticated:
        return user.groups.filter(name="Participant").exists()
    return False

# Create your views here.

def home(request):
    return render(request, "events/home.html")

class EventIndexView(LoginRequiredMixin, View):
    events = Event.objects.select_related("category").prefetch_related("participants")
    categories = Category.objects.all()

    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user) or is_participant(user)

    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        curr_date = timezone.now().date()

        counts = Event.objects.aggregate(
            total=Count('id'),
            upcoming=Count('id', filter=Q(date__gte=curr_date)),
            past=Count('id', filter=Q(date__lt=curr_date))
        )

        events = self.events
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
            "categorys": self.categories,
            "total_count": counts['total'],
            "upcoming_count": counts['upcoming'],
            "past_count": counts['past'],
            "query": query,
            "search_by": search_by,
        }
        return render(request, "events/index.html", context)

class ParticipateEventView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user) or is_participant(user)

    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs.get("id"))
        if request.user in event.participants.all():
            messages.warning(request, "You have already participated in this event")
        else:
            event.participants.add(request.user)
            messages.success(request, "You have successfully participated in this event")
            self._send_mail(request.user, event)
        return redirect("index")

    def _send_mail(self, user, event):
        subject = f"You have successfully participated in {event.name}"
        message = f"Hi {request.user.username},\n\nYou have successfully participated in {event.name} on {event.date} at {event.time} in {event.location}.\nWe look forward to see you there.\n\nBest Regards,\nThe Event.io Team"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]

        if user.email:
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "Participation successfull")
            except:
                messages.warning(request, "Email sending failed")
        else:
            messages.warning(request, "Your account don't have email")

class CancelEventParticipateView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user) or is_participant(user)

    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs.get("id"))
        if request.user in event.participants.all():
            event.participants.remove(request.user)
            messages.success(request, "You have successfully canceled your participation in this event")
            self._send_mail(request.user, event)
        return redirect("index")

    def _send_mail(self, user, event):
        subject = f"Cancelation of participation in {event.name}"
        message = f"Hi {request.user.username},\n\nYou have successfully canceled your participation in {event.name} on {event.date} at {event.time} in {event.location}.\n\nBest Regards,\nThe Event.io Team"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]

        if user.email:
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.warning(request, "Event Participation Cancelled")
            except:
                messages.warning(request, "Email sending failed")
        else:
            messages.warning(request, "You have not participated in this event")

class CreateEventView(LoginRequiredMixin, View):
    events = Event.objects.prefetch_related("participants")
    categorys = Category.objects.all()
    form = EventMForm()
    context = {
        "events": events,
        "categorys": categorys,
        "active_tab": "event",
        "form": form,
    }

    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, "events/event.html", self.context)

    def post(self, request, *args, **kwargs):
        self.form = EventMForm(request.POST, request.FILES)
        if self.form.is_valid():
            self.form.save()
            return redirect("event-create")
        else:
            messages.error(request, "Event not Saved")
            return render(request, "events/event.html", self.context)

class EditEventView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, id):
        event = get_object_or_404(Event, id=id)
        form = EventMForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            form.save()
        return redirect("event-create")

class DeleteEventView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, id):
        event = get_object_or_404(Event, id=id)
        event.delete()
        return redirect("event-create")

class CreateCategoryView(LoginRequiredMixin, View):
    categorys = Category.objects.all()
    form = CategoryMForm()
    context = {
        "categorys": categorys,
        "active_tab": "category",
        "form": form,
    }

    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, "events/category.html", self.context)
    
    def post(self, request):
        self.form = CategoryMForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            return redirect("category-create")
        else:
            messages.error(request, "Category not Saved")
            return redirect("category-create")

class EditCategoryView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, id):
        category = get_object_or_404(Category, id=id)
        form = CategoryMForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
        return redirect("category-create")

class DeleteCategoryView(LoginRequiredMixin, View):
    def _has_permission(self, user):
        return user.is_superuser or is_organizer(user)
    
    def dispatch(self, request, *args, **kwargs):
        if not self._has_permission(request.user):
            messages.error(request, "You do not have permission to access this page, Login first")
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, id):
        category = get_object_or_404(Category, id=id)
        category.delete()
        return redirect("category-create")

class ParticipantListView(LoginRequiredMixin, View):
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

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse("You do not have permission to access this page")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, "events/participant.html", self.context)

class EditParticipantRoleView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse("You do not have permission to access this page")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        user_id = request.POST.get("user_id")
        group_id = request.POST.get("role")

        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)

        user.groups.clear()
        user.groups.add(group)

        self._send_mail(user, group)
        return redirect("participant-list")
    
    def _send_mail(self, user, group):
        subject = "Role chnaged"
        message = f"Hi {user.username},\n\nYour role has been changed to {group.name}.\n\nBest Regards,\nThe Event.io Team"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list) 
        except:
            messages.warning(request, "Email sending failed")

class DeleteParticipantView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse("You do not have permission to access this page")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, id):
        if request.user.id == id:
            messages.warning(request, "You cannot delete yourself")
        else:
            user = User.objects.get(id=id)
            user.delete()
        return redirect("participant-list")