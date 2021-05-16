from django.urls import path
import prediction.views as views
import prediction.file_handler as file_handler

urlpatterns = [
    path('predict/', views.MediaPredict.as_view(), name='api_predict'),
    path('upload/', file_handler.FileHandler.as_view(), name='file_handler'),
]