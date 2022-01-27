from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretalx.common.signals import register_data_exporters
from pretalx.orga.signals import event_copy_data, nav_event_settings


@receiver(nav_event_settings)
def public_voting_settings(sender, request, **kwargs):
    if not request.user.has_perm("orga.change_settings", request.event):
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
    from .exporters import PublicVotingCSVExporter

    return PublicVotingCSVExporter


@receiver(event_copy_data)
def copy_event_settings(sender, other, **kwargs):
    old_settings = getattr(other, "public_vote_settings", None)
    if old_settings:
        old_settings.id = None
        old_settings.event = sender
        old_settings.save()
