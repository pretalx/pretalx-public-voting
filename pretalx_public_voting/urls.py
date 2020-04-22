from django.conf.urls import url
from pretalx.event.models.event import SLUG_CHARS

from . import views

urlpatterns = [
    url(
        fr"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/public_voting/$",
        views.PublicVotingSettings.as_view(),
        name="settings",
    ),
    url(
        f"^(?P<event>[{SLUG_CHARS}]+)/p/voting/signup/$",
        views.SignupView.as_view(),
        name="signup",
    ),
    url(
        f"^(?P<event>[{SLUG_CHARS}]+)/p/voting/thanks/$",
        views.ThanksView.as_view(),
        name="thanks",
    ),
    url(
        f"^(?P<event>[{SLUG_CHARS}]+)/p/voting/talks/(?P<signed_user>[^/]+)/$",
        views.SubmissionListView.as_view(),
        name="talks",
    ),
]
