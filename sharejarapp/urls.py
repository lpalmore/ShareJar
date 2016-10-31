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
    url(r'^makePayment/([a-z | A-Z | 0-9]+)', views.makePayment, name='makePayment'),
    url(r'^confirmPayment(.+)', views.confirmPayment, name='confirmPayment'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
