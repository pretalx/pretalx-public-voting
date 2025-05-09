import random

from django.contrib import messages
from django.db.models import Case, OuterRef, Subquery, When
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django_context_decorator import context
from pretalx.common.views.mixins import PermissionRequired
from pretalx.submission.models import Submission, SubmissionStates

from .exporters import PublicVotingCSVExporter
from .forms import PublicVotingSettingsForm, SignupForm, VoteForm
from .models import PublicVote, PublicVotingSettings
from .utils import event_unsign


class PublicVotingRequired:
    def dispatch(self, request, *args, **kwargs):
        try:
            start = request.event.public_vote_settings.start
            end = request.event.public_vote_settings.end
        except Exception:
            # No settings object exists
            raise Http404()

        _now = now()
        start_valid = (not start) or _now > start
        end_valid = (not end) or _now < end
        if not start_valid or not end_valid:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class SignupView(PublicVotingRequired, FormView):
    template_name = "pretalx_public_voting/signup.html"
    form_class = SignupForm

    def get_success_url(self):
        return reverse("plugins:pretalx_public_voting:thanks", kwargs=self.kwargs)

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["event"] = self.request.event
        result["sid"] = self.request.GET.get("sid")
        return result

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class ThanksView(PublicVotingRequired, TemplateView):
    template_name = "pretalx_public_voting/thanks.html"


class SubmissionListView(PublicVotingRequired, ListView):
    model = Submission
    template_name = "pretalx_public_voting/submission_list.html"
    paginate_by = 20
    context_object_name = "submissions"

    @context
    @cached_property
    def hashed_email(self):
        return event_unsign(self.kwargs["signed_user"], self.request.event)

    def get_queryset(self):
        if not self.hashed_email:
            # If the use wasn't valid, there is no point of returning a
            # QuerySet with the talks
            return None

        votes = PublicVote.objects.filter(
            email_hash=self.hashed_email, submission_id=OuterRef("pk")
        ).values("score")

        # Idea is from https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order/37648265#37648265
        base_qs = self.request.event.submissions.all().filter(
            state=SubmissionStates.SUBMITTED
        )

        # Filter by 'sid' query parameter if provided
        sid = self.request.GET.get("sid")
        if sid:
            base_qs = base_qs.filter(pk=sid)

        tracks = self.request.event.public_vote_settings.limit_tracks.all()
        if tracks:
            base_qs = base_qs.filter(track__in=tracks)
        submission_types = (
            self.request.event.public_vote_settings.limit_submission_types.all()
        )
        if submission_types:
            base_qs = base_qs.filter(submission_type__in=submission_types)
        submission_pks = list(base_qs.values_list("pk", flat=True))
        random.seed(self.hashed_email)
        random.shuffle(submission_pks)
        user_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(submission_pks)]
        )

        return (
            base_qs.annotate(score=Subquery(votes))
            .prefetch_related("speakers")
            .order_by(user_order)
        )

    def get_form_for_submission(self, submission):
        if self.request.method == "POST":
            return VoteForm(
                data=self.request.POST,
                submission=submission,
                hashed_email=self.hashed_email,
                require_score=True,
                initial={"score": submission.score},
                event=self.request.event,
                prefix=submission.code,
            )
        return VoteForm(
            initial={"score": submission.score},
            event=self.request.event,
            prefix=submission.code,
        )

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        sid = self.request.GET.get("sid")
        if sid:
            result["filter_active"] = True
            result["remove_filter_url"] = self.request.path
        else:
            result["filter_active"] = False
        for submission in result["submissions"]:
            submission.vote_form = self.get_form_for_submission(submission)
        return result

    def post(self, request, *args, **kwargs):
        submissions = {
            submission.code: submission for submission in self.get_queryset()
        }
        for key in self.request.POST.keys():
            if "score" not in key:
                continue
            prefix, __ = key.split("-", maxsplit=1)
            submission = submissions.get(prefix)
            if not submission:
                continue
            form = self.get_form_for_submission(submission)
            if form.is_valid():
                # Only save the form if the score has changed
                if form.initial["score"] != form.cleaned_data["score"]:
                    form.save()
        if request.POST.get("action") == "manual":
            messages.success(self.request, _("Thank you for your vote!"))
            return redirect(self.request.path)
        return JsonResponse({})


class PublicVotingSettingsView(PermissionRequired, FormView):
    form_class = PublicVotingSettingsForm
    permission_required = "event.update_event"
    template_name = "pretalx_public_voting/settings.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        settings, _ = PublicVotingSettings.objects.get_or_create(
            event=self.request.event
        )
        return {
            "instance": settings,
            "locales": self.request.event.locales,
            **kwargs,
        }

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["export_url"] = PublicVotingCSVExporter(
            self.request.event
        ).urls.base.full()
        return result
