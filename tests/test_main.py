import datetime as dt

import pytest
from django.core import mail
from django.test import RequestFactory
from django.urls import reverse
from django.utils.timezone import now
from django_scopes import scopes_disabled

from pretalx.event.models import Event
from pretalx_public_voting.exporters import PublicVotingCSVExporter
from pretalx_public_voting.models import PublicVote, PublicVotingSettings
from pretalx_public_voting.signals import copy_event_settings, public_voting_settings
from pretalx_public_voting.utils import event_sign, event_unsign, hash_email

SETTINGS_URL_NAME = "plugins:pretalx_public_voting:settings"
SIGNUP_URL_NAME = "plugins:pretalx_public_voting:signup"
THANKS_URL_NAME = "plugins:pretalx_public_voting:thanks"
TALKS_URL_NAME = "plugins:pretalx_public_voting:talks"


@pytest.mark.django_db
def test_orga_can_access_settings(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_reviewer_cannot_access_settings(review_client, event):
    response = review_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_orga_can_save_settings(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {
            "min_score": "1",
            "max_score": "3",
            "anonymize_speakers": "",
            "show_session_image": "on",
            "show_session_description": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        settings = PublicVotingSettings.objects.get(event=event)
    assert settings.min_score == 1
    assert settings.max_score == 3


@pytest.mark.django_db
def test_settings_rejects_invalid_scores(orga_client, event):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {
            "min_score": "5",
            "max_score": "3",
            "show_session_image": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_signup_page_404_without_settings(client, event):
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": event.slug})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_signup_page_404_outside_window(client, event):
    with scopes_disabled():
        PublicVotingSettings.objects.create(
            event=event,
            start=now() + dt.timedelta(days=1),
            end=now() + dt.timedelta(days=2),
        )
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": event.slug})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_signup_page_accessible_during_window(client, voting_settings):
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": voting_settings.event.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_sends_email(client, voting_settings):
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": voting_settings.event.slug})
    response = client.post(url, {"email": "voter@example.com"}, follow=True)
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert "voter@example.com" in mail.outbox[0].to


@pytest.mark.django_db
def test_signup_rejects_unlisted_email(client, voting_settings):
    voting_settings.allowed_emails = "allowed@example.com"
    voting_settings.save()
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": voting_settings.event.slug})
    response = client.post(url, {"email": "denied@example.com"})
    assert response.status_code == 200
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_signup_allows_listed_email(client, voting_settings):
    voting_settings.allowed_emails = "allowed@example.com"
    voting_settings.save()
    url = reverse(SIGNUP_URL_NAME, kwargs={"event": voting_settings.event.slug})
    response = client.post(url, {"email": "allowed@example.com"}, follow=True)
    assert response.status_code == 200
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_thanks_page(client, voting_settings):
    url = reverse(THANKS_URL_NAME, kwargs={"event": voting_settings.event.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_submission_list_with_valid_link(
    client, voting_settings, submission, signed_email
):
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": voting_settings.event.slug, "signed_user": signed_email},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert submission in response.context["submissions"]


@pytest.mark.django_db
def test_submission_list_with_invalid_link(client, voting_settings, submission):
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": voting_settings.event.slug, "signed_user": "invalid-sig"},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["submissions"]) == 0


@pytest.mark.django_db
def test_vote_submission(client, voting_settings, submission, signed_email):
    event = voting_settings.event
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": event.slug, "signed_user": signed_email},
    )
    response = client.post(
        url,
        {f"{submission.code}-score": "2"},
    )
    assert response.status_code == 200
    with scopes_disabled():
        vote = PublicVote.objects.get(submission=submission)
    assert vote.score == 2


@pytest.mark.django_db
def test_vote_manual_action_redirects(
    client, voting_settings, submission, signed_email
):
    event = voting_settings.event
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": event.slug, "signed_user": signed_email},
    )
    response = client.post(
        url,
        {f"{submission.code}-score": "2", "action": "manual"},
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_vote_updates_existing(client, voting_settings, submission, signed_email):
    event = voting_settings.event
    email_hash = hash_email("voter@example.com", event)
    with scopes_disabled():
        PublicVote.objects.create(submission=submission, email_hash=email_hash, score=1)
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": event.slug, "signed_user": signed_email},
    )
    client.post(url, {f"{submission.code}-score": "3"})
    with scopes_disabled():
        vote = PublicVote.objects.get(submission=submission, email_hash=email_hash)
    assert vote.score == 3


@pytest.mark.django_db
def test_submission_list_filter_by_track(
    client, voting_settings, submission, signed_email, track
):
    submission.track = track
    submission.save()
    url = reverse(
        TALKS_URL_NAME,
        kwargs={"event": voting_settings.event.slug, "signed_user": signed_email},
    )
    response = client.get(url, {"track": [track.pk]})
    assert response.status_code == 200


@pytest.mark.django_db
def test_csv_exporter(event, voting_settings, submission):
    email_hash = hash_email("voter@example.com", event)
    with scopes_disabled():
        PublicVote.objects.create(submission=submission, email_hash=email_hash, score=2)

    exporter = PublicVotingCSVExporter(event)
    with scopes_disabled():
        fieldnames, data = exporter.get_csv_data(request=None)
    assert "code" in fieldnames
    assert len(data) == 1
    assert data[0]["score"] == 2


@pytest.mark.django_db
def test_event_copy_copies_settings(event, voting_settings):
    with scopes_disabled():
        new_event = Event.objects.create(
            name="Copied event",
            is_public=True,
            slug="copied",
            email="orga@orga.org",
            date_from=event.date_from,
            date_to=event.date_to,
            organiser=event.organiser,
        )
    copy_event_settings(sender=new_event, other=event)
    with scopes_disabled():
        new_settings = PublicVotingSettings.objects.get(event=new_event)
    assert new_settings.min_score == voting_settings.min_score
    assert new_settings.max_score == voting_settings.max_score


@pytest.mark.django_db
def test_nav_event_settings_signal(orga_user, event):
    factory = RequestFactory()
    request = factory.get("/")
    request.user = orga_user
    request.event = event
    request.resolver_match = type("Match", (), {"url_name": ""})()
    result = public_voting_settings(sender=event, request=request)
    assert len(result) == 1
    assert result[0]["label"] == "Public voting"


@pytest.mark.django_db
def test_nav_event_settings_hidden_for_reviewer(review_user, event):
    factory = RequestFactory()
    request = factory.get("/")
    request.user = review_user
    request.event = event
    request.resolver_match = type("Match", (), {"url_name": ""})()
    result = public_voting_settings(sender=event, request=request)
    assert result == []


@pytest.mark.django_db
def test_hash_email_deterministic(event):
    h1 = hash_email("test@example.com", event)
    h2 = hash_email("test@example.com", event)
    assert h1 == h2
    assert len(h1) == 32


@pytest.mark.django_db
def test_event_sign_unsign_roundtrip(event):
    data = "test-data"
    signed = event_sign(data, event)
    assert event_unsign(signed, event) == data


@pytest.mark.django_db
def test_event_unsign_invalid(event):
    assert event_unsign("invalid:signature", event) is None
