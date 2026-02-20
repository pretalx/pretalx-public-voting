import datetime as dt

import pytest
from django.core import management
from django.utils.timezone import now
from django_scopes import scopes_disabled

from pretalx.event.models import Event, Organiser, Team
from pretalx.person.models import User
from pretalx.submission.models import Submission, Track

from pretalx_public_voting.models import PublicVotingSettings
from pretalx_public_voting.utils import event_sign, hash_email


@pytest.fixture(scope="session", autouse=True)
def collect_static(request):
    management.call_command("collectstatic", "--noinput", "--clear")


@pytest.fixture
def organiser():
    with scopes_disabled():
        o = Organiser.objects.create(name="Super Organiser", slug="superorganiser")
        Team.objects.create(
            name="Organisers",
            organiser=o,
            can_create_events=True,
            can_change_teams=True,
            can_change_organiser_settings=True,
            can_change_event_settings=True,
            can_change_submissions=True,
        )
        Team.objects.create(name="Reviewers", organiser=o, is_reviewer=True)
    return o


@pytest.fixture
def event(organiser):
    today = dt.date.today()
    with scopes_disabled():
        event = Event.objects.create(
            name="Fancy testevent",
            is_public=True,
            slug="test",
            email="orga@orga.org",
            date_from=today,
            date_to=today + dt.timedelta(days=3),
            organiser=organiser,
        )
        event.enable_plugin("pretalx_public_voting")
        event.save()
        for team in organiser.teams.all():
            team.limit_events.add(event)
    return event


@pytest.fixture
def voting_settings(event):
    with scopes_disabled():
        settings, _ = PublicVotingSettings.objects.get_or_create(
            event=event,
            defaults={
                "start": now() - dt.timedelta(days=1),
                "end": now() + dt.timedelta(days=1),
                "min_score": 1,
                "max_score": 3,
            },
        )
    return settings


@pytest.fixture
def submission(event):
    with scopes_disabled():
        return Submission.objects.create(
            event=event,
            title="Test Submission",
            submission_type=event.submission_types.first(),
            state="submitted",
        )


@pytest.fixture
def track(event):
    with scopes_disabled():
        return Track.objects.create(event=event, name="Test Track")


@pytest.fixture
def signed_email(event):
    email = "voter@example.com"
    email_hash = hash_email(email, event)
    return event_sign(email_hash, event)


@pytest.fixture
def orga_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="orgapassw0rd",
            email="orgauser@orga.org",
            name="Orga User",
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=True, is_reviewer=False
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def review_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="reviewpassw0rd",
            email="reviewuser@orga.org",
            name="Review User",
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=False, is_reviewer=True
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def orga_client(orga_user, client):
    client.force_login(orga_user)
    return client


@pytest.fixture
def review_client(review_user, client):
    client.force_login(review_user)
    return client
