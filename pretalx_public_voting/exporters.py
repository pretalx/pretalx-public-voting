from defusedcsv import csv

from django.http import Http404, HttpResponse

from .models import PublicVote


def get_data(event):
    fieldnames = ["code", "voter", "timestamp", "score"]
    data = []
    qs = PublicVote.objects.filter(
        submission__event = event
    ).order_by("submission__code")
    for vote in qs:
        data.append(
            {
                "code": vote.submission.code,
                "voter": vote.email_hash,
                "timestamp": vote.timestamp,
                "score": vote.score,
            }
        )

    return fieldnames, data

def csv_export(request, event):
    if not request.user.has_perm("orga.change_settings", request.event):
        raise Http404()

    filename = "voting.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    fieldnames, data = get_data(request.event)
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    return response
