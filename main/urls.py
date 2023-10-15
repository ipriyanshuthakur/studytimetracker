from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>', views.sub_list, name='sub_list'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('start_subject/<int:pk>', views.start_subject, name='start_subject'),
    path('mark_complete/<int:pk>', views.mark_complete, name='mark_complete'),
    path('add_record/', views.add_record, name='add_record'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('setting_page/', views.setting_page, name='setting_page'),
    path('progress/', views.progress, name='progress'),
    path('date_range_records/<str:start>/<str:end>/', views.date_range_view, name='date_range_view'),
    path('search_page/', views.search_page, name='search_page'),
    path('records_progress/<str:sDate>/', views.records_progress, name='records_progress'),




]
