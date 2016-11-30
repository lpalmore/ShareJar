from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^$', views.home, name='adminHome'),
    url(r'^joinTeam', views.joinTeam, name='joinTeam'),
    url(r'^teamStats/$', views.teamStats, name='teamStats'),
    url(r'^teamStats/(?P<teamName>[a-z | A-Z | 0-9]+)', views.teamStats, name='teamStats'),
    url(r'^teamStats', views.teamStats, name='teamStats'),
    url(r'^balance', views.balance, name='balance'),
    url(r'^createUser', views.createUser, name='createUser'),
    url(r'^addCharity', views.addCharity, name='addCharity'),
    url(r'^removeCharity', views.removeCharity, name='removeCharity'),
    url(r'^confirmRemoveCharity/([a-z | A-Z | 0-9]+)', views.confirmRemoveCharity, name='confirmRemoveCharity'),
    url(r'^lookupCharity', views.lookupCharity, name='lookupCharity'),
    url(r'^editCharity/([a-z | A-Z | 0-9]+)', views.editCharity, name='editCharity'),
    url(r'^deleteAccount', views.deleteAccount, name='deleteAccount'),
    url(r'^confirmDeleteAccount/([a-z | A-Z | 0-9]+)', views.confirmDeleteAccount, name='confirmDeleteAccount'),
    url(r'^editBalance', views.editBalance, name='editBalance'),
    url(r'^makePayment/([a-z | A-Z | 0-9]+)', views.makePayment, name='makePayment'),
    url(r'^confirmPayment(.+)', views.confirmPayment, name='confirmPayment'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
