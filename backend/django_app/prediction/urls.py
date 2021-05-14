from django.urls import path
import prediction.views as views

urlpatterns = [
    path('predict/', views.MediaPredict.as_view(), name='api_predict'),
]