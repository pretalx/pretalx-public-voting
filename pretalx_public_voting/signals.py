from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from pretalx.common.signals import register_data_exporters
from pretalx.orga.signals import event_copy_data, nav_event_settings

from .models import PublicVotingSettings


@receiver(nav_event_settings)
def public_voting_settings(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        return []
    return [
        {
            "label": _("Public voting"),
            "url": reverse(
                "plugins:pretalx_public_voting:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_public_voting:settings",
        }
    ]


@receiver(register_data_exporters)
def register_data_exporter(sender, **kwargs):
    from .exporters import PublicVotingCSVExporter  # noqa: PLC0415

    return PublicVotingCSVExporter


@receiver(event_copy_data)
def copy_event_settings(
    sender, other, track_map=None, submission_type_map=None, **kwargs
):
    old_settings = PublicVotingSettings.objects.filter(
        event__slug__iexact=other
    ).first()
    if not old_settings:
        return
    delta = sender.date_from - old_settings.event.date_from
    track_pks = list(old_settings.limit_tracks.values_list("pk", flat=True))
    type_pks = list(old_settings.limit_submission_types.values_list("pk", flat=True))
    old_settings.id = None
    old_settings.event = sender
    if old_settings.start:
        old_settings.start += delta
    if old_settings.end:
        old_settings.end += delta
    old_settings.save()
    old_settings.limit_tracks.set([track_map[pk] for pk in track_pks])
    old_settings.limit_submission_types.set(
        [submission_type_map[pk] for pk in type_pks]
    )
