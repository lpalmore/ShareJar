from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from sharejarapp.views import HomePageView, BalancePageView, JoinTeamView
from django.contrib.auth.decorators import login_required
urlpatterns = [
    url(r'^$', login_required(HomePageView.as_view()), name='home'),
    url(r'^$', login_required(HomePageView.as_view()), name='home'),
    url(r'^joinTeam', login_required(JoinTeamView.as_view()), name='joinTeam'),
    url(r'^teamStats/$', views.teamStats, name='teamStats'),
    url(r'^teamStats/(?P<teamName>[a-z | A-Z | 0-9]+)', views.teamStats, name='teamStats'),
    url(r'^teamStats', views.teamStats, name='teamStats'),
    url(r'^balance', login_required(BalancePageView.as_view()), name='balance'),
    url(r'^createUser', views.createUser, name='createUser'),
    url(r'^addCharity', views.addCharity, name='addCharity'),
    url(r'^removeCharity', views.removeCharity, name='removeCharity'),
    url(r'^confirmRemoveCharity/([a-z | A-Z | 0-9]+)', views.confirmRemoveCharity, name='confirmRemoveCharity'),
    url(r'^lookupCharity', views.lookupCharity, name='lookupCharity'),
    url(r'^editCharity/([a-z | A-Z | 0-9]+)', views.editCharity, name='editCharity'),
    url(r'^deleteAccount', views.deleteAccount, name='deleteAccount'),
    url(r'^confirmDeleteAccount/(?P<charity>[a-z | A-Z | 0-9]+)', views.confirmDeleteAccount, name='confirmDeleteAccount'),
    url(r'^makePayment/(?P<charity>[a-z | A-Z | 0-9]+)/(?P<team>[a-z | A-Z | 0-9]+)', views.makePayment, name='makePayment'),
    url(r'^makePayment/([a-z | A-Z | 0-9]+)', views.makePayment, name='makePayment'),
    url(r'^confirmPayment(.+)', views.confirmPayment, name='confirmPayment'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
