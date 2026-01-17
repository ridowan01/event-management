from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # user section
    path("index/", views.index, name="index"),
    path("participate/<int:id>/", views.partipateEvent, name="participate-event"),
    path("participate/cancel/<int:id>/", views.cancelPartipateEvent, name="cancel-participate-event"),

    # organizer and admin section
    # event section
    path("event/create/", views.eventCreate, name="event-create"),
    path("event/edit/<int:id>/", views.eventEdit, name="event-edit"),
    path("event/delete/<int:id>/", views.eventDelete, name="event-delete"),
    
    # category section
    path("category/create/", views.categoryCreate, name="category-create"),
    path("category/edit/<int:id>/", views.categoryEdit, name="category-edit"),
    path("category/delete/<int:id>/", views.categoryDelete, name="category-delete"),

    # admin section
    # participant section
    path("participant/list/", views.participantList, name="participant-list"),
    path("participant/role/edit/", views.participantRoleEdit, name="participant-role-edit"),
    path("participant/delete/<int:id>/", views.participantDelete, name="participant-delete"),
]
