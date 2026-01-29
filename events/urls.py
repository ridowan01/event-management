from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # user section
    path("index/", views.EventIndexView.as_view(), name="index"),
    path("participate/<int:id>/", views.ParticipateEventView.as_view(), name="participate-event"),
    path("participate/cancel/<int:id>/", views.CancelEventParticipateView.as_view(), name="cancel-participate-event"),

    # organizer and admin section
    # event section
    path("event/create/", views.CreateEventView.as_view(), name="event-create"),
    path("event/edit/<int:id>/", views.EditEventView.as_view(), name="event-edit"),
    path("event/delete/<int:id>/", views.DeleteEventView.as_view(), name="event-delete"),
    
    # category section
    path("category/create/", views.CreateCategoryView.as_view(), name="category-create"),
    path("category/edit/<int:id>/", views.EditCategoryView.as_view(), name="category-edit"),
    path("category/delete/<int:id>/", views.DeleteCategoryView.as_view(), name="category-delete"),

    # admin section
    # participant section
    path("participant/list/", views.ParticipantListView.as_view(), name="participant-list"),
    path("participant/role/edit/", views.EditParticipantRoleView.as_view(), name="participant-role-edit"),
    path("participant/delete/<int:id>/", views.DeleteParticipantView.as_view(), name="participant-delete"),
]
