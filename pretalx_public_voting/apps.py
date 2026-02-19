from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_public_voting"
    verbose_name = "pretalx public voting plugin"

    class PretalxPluginMeta:
        name = gettext_lazy("pretalx public voting plugin")
        author = "Tobias Kunze"
        description = gettext_lazy("A public voting plugin for pretalx")
        visible = True
        version = __version__
        category = "FEATURE"
        settings_links = [
            (gettext_lazy("Settings"), "plugins:pretalx_public_voting:settings", {}),
        ]

    def ready(self):
        from . import signals  # NOQA
