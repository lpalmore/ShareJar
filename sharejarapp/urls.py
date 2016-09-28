from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^joinTeam', views.joinTeam, name='joinTeam'),
    url(r'^teamStats', views.teamStats, name='teamStats'),
    url(r'^addBalance', views.addBalance, name='addBalance'),
    url(r'^currentBalance', views.currentBalance, name='currentBalance'),
    url(r'^createUser', views.createUser, name='createUser'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
