from django.db import models
from django.utils.translation import gettext_lazy as _
from django_scopes import ScopedManager


class PublicVote(models.Model):
    score = models.IntegerField(verbose_name=_("Score"))
    submission = models.ForeignKey(
        to="submission.Submission",
        related_name="public_votes",
        on_delete=models.CASCADE,
    )
    # The hashed email addresses are always 16 bytes long => 32 characters
    email_hash = models.CharField(max_length=32, blank=False)
    timestamp = models.DateTimeField(auto_now=True)

    objects = ScopedManager(event="submission__event")

    class Meta:
        unique_together = (("submission", "email_hash"),)

    def __str__(self):
        return f"Vote(score={self.score}, email_hash={self.email_hash}, timestamp={self.timestamp}, submission={self.submission.title})"
