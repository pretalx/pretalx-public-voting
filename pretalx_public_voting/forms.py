from django import forms
from django.utils.translation import gettext_lazy as _
from django_scopes.forms import SafeModelMultipleChoiceField
from i18nfield.forms import I18nModelForm
from pretalx.common.forms.renderers import InlineFormLabelRenderer, InlineFormRenderer
from pretalx.common.forms.widgets import EnhancedSelectMultiple, HtmlDateTimeInput
from pretalx.common.urls import build_absolute_uri
from pretalx.mail.models import QueuedMail

from .models import PublicVote, PublicVotingSettings
from .utils import event_sign, hash_email


class SignupForm(forms.Form):
    default_renderer = InlineFormLabelRenderer

    email = forms.EmailField(required=True)

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not self.event.public_vote_settings.allowed_email_list:
            return email
        if email.strip().lower() in self.event.public_vote_settings.allowed_email_list:
            return email
        raise forms.ValidationError(_("This address is not allowed to cast a vote."))

    def send_email(self):
        event = self.event
        email_hashed = hash_email(self.cleaned_data["email"], event)
        email_signed = event_sign(email_hashed, event)

        # For the email link, sign the hashed email address, so that no one
        # can just randomly create new URLs and pretend to be a user that
        # was validated via email. Credits for the email signing code go
        # to Volker Mische / @vmx
        vote_url = build_absolute_uri(
            "plugins:pretalx_public_voting:talks",
            kwargs={"event": event.slug, "signed_user": email_signed},
        )

        mail_text = _(
            """Hi,

you have registered to vote for submissions for {event.name}.
Please confirm that this email address is valid by following this link:

{vote_url}

If you did not register for voting, you can ignore this email.

Thank you for participating in the vote!

The {event.name} organisers
"""
        )
        QueuedMail(
            event=event,
            to=self.cleaned_data["email"],
            subject=_("Public voting registration"),
            text=str(mail_text).format(vote_url=vote_url, event=event),
        ).send()


class VoteForm(forms.Form):
    default_renderer = InlineFormRenderer

    def __init__(
        self,
        *args,
        event=None,
        submission=None,
        hashed_email=None,
        require_score=False,
        **kwargs,
    ):
        self.event = event
        self.submission = submission
        self.hashed_email = hashed_email
        super().__init__(*args, **kwargs)
        self.min_value = event.public_vote_settings.min_score
        self.max_value = event.public_vote_settings.max_score
        choices = []
        for counter in range(abs(self.max_value - self.min_value) + 1):
            value = self.min_value + counter
            name = event.public_vote_settings.score_names.get(str(value)) or value
            choices.append((str(value), name))
        self.fields["score"] = forms.ChoiceField(
            choices=choices,
            required=require_score,
            widget=forms.RadioSelect,
        )
        self.fields["score"].widget.attrs["autocomplete"] = "off"

    def clean_score(self):
        score = int(self.cleaned_data.get("score"))
        if not self.min_value <= score <= self.max_value:
            raise forms.ValidationError(
                _(
                    f"Please assign a score between {self.min_value} and {self.max_value}!"
                )
            )
        return score

    def save(self):
        return PublicVote.objects.update_or_create(
            submission=self.submission,
            email_hash=self.hashed_email,
            defaults={"score": self.cleaned_data["score"]},
        )


class PublicVotingSettingsForm(I18nModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["limit_tracks"].queryset = self.instance.event.tracks.all()
        minimum = self.instance.min_score
        maximum = self.instance.max_score
        for number in range(abs(maximum - minimum + 1)):
            index = minimum + number
            self.fields[f"score_name_{index}"] = forms.CharField(
                label=_("Score label ({})").format(index),
                help_text=_(
                    'Human readable explanation of what a score of "{}" actually means, e.g. "great!".'
                ).format(index),
                required=False,
                initial=self.instance.score_names.get(str(index)),
            )

    def clean(self):
        data = self.cleaned_data
        minimum = int(data.get("min_score"))
        maximum = int(data.get("max_score"))
        if minimum >= maximum:
            self.add_error(
                "min_score",
                forms.ValidationError(
                    _("Please assign a minimum score smaller than the maximum score!")
                ),
            )
        return data

    def save(self, *args, **kwargs):
        instance = super().save()
        for number in range(abs(instance.max_score - instance.min_score + 1)):
            index = instance.min_score + number
            instance.score_names[index] = self.cleaned_data.get(f"score_name_{index}")
        instance.save()
        return instance

    class Meta:
        model = PublicVotingSettings
        fields = (
            "start",
            "end",
            "text",
            "anonymize_speakers",
            "show_session_image",
            "show_session_description",
            "limit_tracks",
            "allowed_emails",
            "min_score",
            "max_score",
        )
        widgets = {
            "start": HtmlDateTimeInput,
            "end": HtmlDateTimeInput,
            "limit_tracks": EnhancedSelectMultiple(color_field="color"),
        }
        field_classes = {
            "limit_tracks": SafeModelMultipleChoiceField,
        }
