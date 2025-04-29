#!/bin/bash


# Install local plugin
python -m pip install -e .


# Apply migrations
python3 -m pretalx migrate
