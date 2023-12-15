from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_scopes import ScopedManager
from i18nfield.fields import I18nTextField
from pretalx.common.phrases import phrases


def get_dict():
    return {}


class PublicVotingSettings(models.Model):
    event = models.OneToOneField(
        to="event.Event", related_name="public_vote_settings", on_delete=models.CASCADE
    )

    start = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "No public votes will be possible before this time. Submissions will not be publicly visible."
        ),
        verbose_name=_("Start"),
    )
    end = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "No public votes will be possible after this time. Submissions will not be publicly visible."
        ),
        verbose_name=_("End"),
    )
    text = I18nTextField(
        null=True,
        blank=True,
        verbose_name=_("Text"),
        help_text=_("This text will be shown at the top of the public voting page.")
        + " "
        + phrases.base.use_markdown,
    )
    anonymize_speakers = models.BooleanField(
        verbose_name=_("Anonymise content"),
        help_text=_("Hide speaker names and use anonymized content where available?"),
        default=False,
    )
    show_session_image = models.BooleanField(
        verbose_name=_("Show session image"),
        help_text=_("Show the session image if one was uploaded."),
        default=True,
    )
    show_session_description = models.BooleanField(
        verbose_name=_("Show session description"),
        help_text=_(
            "By default, only the abstract of each session is listed. By enabling this, the longer description text will also be shown."
        ),
        default=False,
    )
    min_score = models.IntegerField(
        default=1,
        verbose_name=_("Minimum score"),
        help_text=_("The minimum score voters can assign"),
    )
    max_score = models.IntegerField(
        default=3,
        verbose_name=_("Maximum score"),
        help_text=_("The maximum score voters can assign"),
    )
    score_names = models.JSONField(default=get_dict)
    allowed_emails = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Allowed emails"),
        help_text=_(
            "You can limit who is allowed to cast a vote. Please enter one email address per line."
        ),
    )
    limit_tracks = models.ManyToManyField(
        to="submission.Track", verbose_name=_("Limit to tracks"), blank=True
    )
    limit_submission_types = models.ManyToManyField(
        to="submission.SubmissionType",
        verbose_name=_("Limit to session types"),
        blank=True,
        help_text=_("If no session type is selected, then all submission are shown."),
    )

    @cached_property
    def allowed_email_list(self):
        allowed = (self.allowed_emails or "").strip().lower()
        if not allowed:
            return []
        return {mail.strip() for mail in allowed.split("\n")}


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
