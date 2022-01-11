pretalx public voting plugin
============================

This is a plugin for `pretalx`_, allowing attendees (or anybody interested) to vote on submitted proposals.

Changelog
---------

v0.2.1, 2021-12-07
~~~~~~~~~~~~~~~~~~

- Added compatibility with the latest pretalx release
- Fixed a bug involving salt lengths

v0.2.0, 2021-03-11
~~~~~~~~~~~~~~~~~~

- Added a CSV export of voting results
- Added an indicator of the vote being saved
- Added localisation (multi-language support) to settings
- Optionally hide session images
- Added a German translation
- Added start and end time settings

v0.1.0, 2020-04-23
~~~~~~~~~~~~~~~~~~

Initial release

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-public-voting``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretalx's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2020 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
