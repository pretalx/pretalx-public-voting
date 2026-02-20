pretalx public voting plugin
============================

.. image:: https://raw.githubusercontent.com/pretalx/pretalx-public-voting/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-public-voting/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Coverage

This is a plugin for `pretalx`_, allowing attendees (or anybody interested) to vote on submitted proposals.

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-public-voting``.

3. Install the plugin in editable mode: ``uv pip install -e .``

4. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


Testing
~~~~~~~

Run ``just test`` to execute the test suite. This will automatically install pretalx from git if it's not already present.

If you're developing against a local pretalx checkout, use ``just install-pretalx-local /path/to/pretalx`` first.

Use ``just fmt`` to format your code, or ``just fmt-check`` to check formatting without modifying files.


License
-------

Copyright 2020 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
