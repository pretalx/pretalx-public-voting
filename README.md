# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-public-voting/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| pretalx\_public\_voting/\_\_init\_\_.py |        1 |        0 |        0 |        0 |    100% |           |
| pretalx\_public\_voting/apps.py         |       15 |        0 |        0 |        0 |    100% |           |
| pretalx\_public\_voting/exporters.py    |       16 |        1 |        0 |        0 |     94% |        16 |
| pretalx\_public\_voting/forms.py        |      106 |        5 |       22 |        5 |     92% |55, 113, 211, 217, 232 |
| pretalx\_public\_voting/models.py       |       36 |        0 |        2 |        0 |    100% |           |
| pretalx\_public\_voting/signals.py      |       20 |        1 |        4 |        1 |     92% |30, 36->exit |
| pretalx\_public\_voting/utils.py        |       12 |        0 |        0 |        0 |    100% |           |
| pretalx\_public\_voting/views.py        |      132 |        6 |       28 |        7 |     92% |106, 111, 116, 119->122, 163-164, 187, 189->181 |
| **TOTAL**                               |  **338** |   **13** |   **56** |   **13** | **93%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/pretalx/pretalx-public-voting/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-public-voting/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pretalx/pretalx-public-voting/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-public-voting/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fpretalx%2Fpretalx-public-voting%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-public-voting/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.