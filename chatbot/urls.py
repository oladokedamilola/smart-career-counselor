from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path('new/', views.start_new_chat, name='start_new_chat'),
    path('session/<uuid:session_id>/', views.load_session, name='load_session'),

    path('chat/n/', views.send_first_message, name='send_first_message'),


    path('rename/<uuid:session_id>/', views.rename_session, name='rename_session'),
    path('delete/<uuid:session_id>/', views.delete_session, name='delete_session'),



]
