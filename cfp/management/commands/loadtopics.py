# Copyright 2011 Thierry Carrez <thierry@openstack.org>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

from django.core.management.base import BaseCommand, CommandError
from cfp.models import Topic


class Command(BaseCommand):
    args = '<description.json>'
    help = 'Create topics from JSON description'

    def handle(self, *args, **options):

        if len(args) != 1:
            raise CommandError('Incorrect arguments')

        try:
            with open(args[0]) as f:
                data = json.load(f)
        except ValueError as exc:
            raise CommandError("Malformed JSON: %s" % exc.message)

        for topicname, desc in data.iteritems():
            t = Topic(name=topicname, lead_username=desc['lead_username'],
                      description=desc['description'])
            t.save()
