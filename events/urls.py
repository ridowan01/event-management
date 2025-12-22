from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # event section
    path("event/create/", views.eventCreate, name="event-create"),
    path("event/edit/<int:id>/", views.eventEdit, name="event-edit"),
    path("event/delete/<int:id>/", views.eventDelete, name="event-delete"),
    
    # category section
    path("category/create/", views.categoryCreate, name="category-create"),
    path("category/edit/<int:id>/", views.categoryEdit, name="category-edit"),
    path("category/delete/<int:id>/", views.categoryDelete, name="category-delete"),

    # participants section
    path("participant/create/", views.participantCreate, name="participant-create"),
    path("participant/edit/<int:id>/", views.participantEdit, name="participant-edit"),
    path("participant/delete/<int:id>/", views.participantDelete, name="participant-delete")
]
