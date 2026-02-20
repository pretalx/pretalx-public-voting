from django.utils.translation import gettext_lazy as _

from pretalx.common.exporter import BaseExporter, CSVExporterMixin

from .models import PublicVote


class PublicVotingCSVExporter(CSVExporterMixin, BaseExporter):
    public = False
    icon = "fa-list"
    filename_identifier = "public_votes"
    cors = "*"

    @property
    def verbose_name(self):
        return _("Public Voting CSV")

    def get_csv_data(self, request, **kwargs):
        fieldnames = ["code", "voter", "timestamp", "score"]
        votes = (
            PublicVote.objects.filter(submission__event=self.event)
            .order_by("submission__code")
            .select_related("submission")
        )
        data = [
            {
                "code": vote.submission.code,
                "voter": vote.email_hash,
                "timestamp": vote.timestamp.isoformat(),
                "score": vote.score,
            }
            for vote in votes
        ]

        return fieldnames, data
