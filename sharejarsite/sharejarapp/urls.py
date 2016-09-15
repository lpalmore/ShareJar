from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^joinTeam', views.joinTeam, name='joinTeam'),
    url(r'^teamStats', views.teamStats, name='teamStats'),
    url(r'^addBalance', views.addBalance, name='addBalance'),
    url(r'^currentBalance', views.currentBalance, name='currentBalance'),
]
