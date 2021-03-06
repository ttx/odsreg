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

from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    (r'^openid/', include('django_openid_auth.urls')),
    (r'^$', 'odsreg.cfp.views.list'),
    (r'^cfp/', include('odsreg.cfp.urls')),
    (r'^scheduling/', include('odsreg.scheduling.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^logout$', 'odsreg.cfp.views.dologout'),
)
