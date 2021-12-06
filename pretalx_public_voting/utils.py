from contextlib import suppress
from hashlib import blake2b

from django.core import signing


def hash_email(email, event):
    return blake2b(
        email.encode("utf-8"),
        salt=event.slug.encode("utf-8")[:16],
        digest_size=16,
    ).hexdigest()


def event_sign(data, event):
    signer = signing.Signer(salt=event.slug)
    return signer.sign(data)


def event_unsign(data, event):
    signer = signing.Signer(salt=event.slug)
    with suppress(signing.BadSignature):
        return signer.unsign(data)
