odsreg - The OpenStack Design Summit session management system
==============================================================

odsreg is the Django app used for the OpenStack Design Summit
session proposal and scheduling.

It has the following features:

 * Session proposal
 * Session review
 * Ability to merge sessions and add a cover description
 * Drag-and-drop scheduling
 * Synchronization to sched.org event schedule
 * Launchpad SSO integration


Prerequisites
-------------

You'll need the following Python modules installed:
 - django (1.4+)
 - python-django-auth-openid


Configuration and Usage
-----------------------

Copy local_settings.py.sample to local_settings.py and change
settings there.

Create empty database:
./manage.py syncdb

Copy topics.json.sample to topics.json and edit the file to match
the topics you want to have. Then run:

./manage.py loadtopics topics.json

Then run a dev server using:
./manage.py runserver

When you have room layout, copy slots.json.sample to slots.json and edit
the file to match the rooms and time slots for each topic. Then run:

./manage.py loadslots slots.json
