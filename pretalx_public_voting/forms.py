from django import forms
from django.utils.translation import gettext_lazy as _
from hierarkey.forms import HierarkeyForm
from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.forms import I18nFormMixin

from pretalx.common.phrases import phrases
from pretalx.common.urls import build_absolute_uri
from pretalx.mail.models import QueuedMail

from .models import PublicVote
from .utils import event_sign, hash_email


class SignupForm(forms.Form):
    email = forms.EmailField(required=True)

    def send_email(self, event):
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
        mail_text = f"""Hi,

you have registered to vote for submissions for {event.name}.
Please confirm that this email address is valid by following this link:

    {vote_url}

If you did not register for voting, you can ignore this email.

Thank you for participating in the vote!
The organiser team
"""
        QueuedMail(
            event=event,
            to=self.cleaned_data["email"],
            subject=_("Public voting registration"),
            text=mail_text,
        ).send()


class VoteForm(forms.Form):
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
        self.min_value = int(event.settings.public_voting_min_score)
        self.max_value = int(event.settings.public_voting_max_score)
        choices = []
        for counter in range(abs(self.max_value - self.min_value) + 1):
            value = self.min_value + counter
            name = event.settings.get(f"public_voting_score_name_{value}") or value
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


class PublicVotingSettingsForm(I18nFormMixin, HierarkeyForm):

    public_voting_text = I18nFormField(
        help_text=_(
            "This text will be shown at the top of the public voting page."
        )
        + " "
        + phrases.base.use_markdown,
        label=_("Text"),
        widget=I18nTextarea,
        required=False,
    )
    public_voting_start = forms.DateTimeField(
        help_text=_(
            "No public votes will be possible before this time. Submissions will not be publicly visible."
        ),
        label=_("Start"),
        widget=forms.DateTimeInput(attrs={"class": "datetimepickerfield"}),
    )
    public_voting_end = forms.DateTimeField(
        help_text=_(
            "No public votes will be possible after this time. Submissions will not be publicly visible."
        ),
        label=_("End"),
        widget=forms.DateTimeInput(attrs={"class": "datetimepickerfield"}),
    )
    public_voting_anonymize_speakers = forms.BooleanField(
        required=False,
        label=_("Anonymise content"),
        help_text=_("Hide speaker names and use anonymized content where available?"),
    )
    public_voting_show_session_image = forms.BooleanField(
        required=False,
        label=_("Show session image"),
        help_text=_("Show the session image if one was uploaded."),
        initial=True,
    )
    public_voting_min_score = forms.IntegerField(
        label=_("Minimum score"),
        help_text=_("The minimum score voters can assign"),
        initial=1,
    )
    public_voting_max_score = forms.IntegerField(
        label=_("Maximum score"),
        help_text=_("The maximum score voters can assign"),
        initial=3,
    )

    def __init__(self, obj, *args, **kwargs):
        super().__init__(*args, obj=obj, **kwargs)
        minimum = obj.settings.public_voting_min_score
        maximum = obj.settings.public_voting_max_score
        minimum = int(minimum) if minimum is not None else 1
        maximum = int(maximum) if maximum is not None else 3
        for number in range(abs(maximum - minimum + 1)):
            index = minimum + number
            self.fields[f"public_voting_score_name_{index}"] = forms.CharField(
                label=_("Score label ({})").format(index),
                help_text=_(
                    'Human readable explanation of what a score of "{}" actually means, e.g. "great!".'
                ).format(index),
                required=False,
            )

    def clean(self):
        data = self.cleaned_data
        minimum = int(data.get("public_voting_min_score"))
        maximum = int(data.get("public_voting_max_score"))
        if minimum >= maximum:
            self.add_error(
                "public_voting_min_score",
                forms.ValidationError(
                    _("Please assign a minimum score smaller than the maximum score!")
                ),
            )
        return data
