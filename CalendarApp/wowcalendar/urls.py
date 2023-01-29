from django.urls import path

from . import views

urlpatterns = [
    path('', views.homePage, name='home'),
    path('logout/', views.request_logout, name='logout'),
    path('characters/', views.characterPage, name='characters'),
    path('characters/add', views.characterAddPage, name='charactersAdd'),
    path('characters/edit/<int:char_id>', views.characterEditPage, name='charactersEdit'),
    path('classes/', views.classPage, name='classes'),
    path('classes/add', views.classAddPage, name='classAdd'),
    path('calendar/', views.calendarPage, name='calendarPage'),
    path('calendar/add', views.eventAddPage, name='eventAdd'),
    path('calendar/view', views.eventViewPage, name='eventView'),
    path('calendar/edit/<int:event_id>', views.eventEditPage, name='eventEdit'),
    path('manage/', views.manageUsersPage, name='manageUsers'),
    path('manage/user', views.changeUserPage, name='changeUser'),
    path('account/', views.accountPage, name='account'),
    path('calendar/list', views.eventListPage, name='eventList'),
    path('templates/', views.templatePage, name='templates'),
    path('templates/add', views.templateAddPage, name='templateAdd'),
    path('templates/edit/<int:template_id>', views.templateEditPage, name='templateEdit'),
    path('template/data', views.getTemplateData, name='templateData'),
]