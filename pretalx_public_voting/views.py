import random

from django.contrib import messages
from django.db.models import Case, OuterRef, Subquery, When
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django_context_decorator import context
from pretalx.common.mixins.views import PermissionRequired
from pretalx.submission.models import Submission

from .forms import PublicVotingSettingsForm, SignupForm, VoteForm
from .models import PublicVote
from .utils import event_unsign


class SignupView(FormView):
    template_name = "pretalx_public_voting/signup.html"
    form_class = SignupForm

    def get_success_url(self):
        return reverse("plugins:pretalx_public_voting:thanks", kwargs=self.kwargs)

    def form_valid(self, form):
        form.send_email(self.request.event)
        return super().form_valid(form)


class ThanksView(TemplateView):
    template_name = "pretalx_public_voting/thanks.html"


class SubmissionListView(ListView):
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
        submission_pks = list(Submission.objects.all().values_list("pk", flat=True))
        random.seed(self.hashed_email)
        random.shuffle(submission_pks)
        user_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(submission_pks)]
        )

        return (
            Submission.objects.all()
            .annotate(score=Subquery(votes))
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
        for submission in result["submissions"]:
            submission.vote_form = self.get_form_for_submission(submission)
        return result

    def post(self, request, *args, **kwargs):
        submissions = {
            submission.code: submission for submission in self.get_queryset()
        }
        for key, value in self.request.POST.items():
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


class PublicVotingSettings(PermissionRequired, FormView):
    form_class = PublicVotingSettingsForm
    permission_required = "orga.change_settings"
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
        return {
            "obj": self.request.event,
            "attribute_name": "settings",
            "locales": self.request.event.locales,
            **kwargs
        }
