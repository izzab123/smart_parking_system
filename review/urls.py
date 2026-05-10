from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('all/', views.all_reviews, name='all_reviews'),
]