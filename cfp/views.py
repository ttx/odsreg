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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.encoding import smart_str
from odsreg.cfp.models import Proposal, Topic
from odsreg.cfp.models import ProposalForm, ProposalEditForm
from odsreg.cfp.models import ProposalReviewForm, ProposalSwitchForm


def linkify(blueprints):
    links = {}
    for bp in blueprints.split():
        (project, name) = bp.split('/')
        links[bp] = "https://blueprints.launchpad.net/%s/+spec/%s" \
                 % (project, name)
    return links


def topiclead(user, topic):
    return (user.username == topic.lead_username) or user.is_staff


def forbidden():
    return HttpResponseForbidden("Forbidden")


@login_required
def list(request):
    proposals = Proposal.objects.all()
    reviewable_topics = Topic.objects.filter(
        lead_username=request.user.username)
    request.session['lastlist'] = ""
    return render_to_response("cfplist.html",
                              {'req': request,
                               'proposals': proposals,
                               'reviewable_topics': reviewable_topics})


@login_required
def topiclist(request, topicid):
    topic = Topic.objects.get(id=topicid)
    if not topiclead(request.user, topic):
        return forbidden()
    proposals = Proposal.objects.filter(topic=topicid)
    request.session['lastlist'] = "cfp/topic/%s" % topicid
    return render_to_response("topiclist.html",
                              {'req': request,
                               'proposals': proposals,
                               'topic': topic})


@login_required
def topicstatus(request):
    topics = Topic.objects.all()
    return render_to_response("topicstatus.html",
                              {'req': request,
                               'topics': topics})


@login_required
def details(request, proposalid):
    proposal = Proposal.objects.get(id=proposalid)
    return render_to_response("cfpdetails.html",
                              {'req': request,
                               'proposal': proposal,
                               'blueprints': linkify(proposal.blueprints)})


@login_required
def create(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.proposer = request.user
            proposal.status = 'U'
            proposal.save()
            return list(request)
    else:
        form = ProposalForm()

    topics = Topic.objects.all()
    return render_to_response('cfpcreate.html',
                              {'req': request,
                               'topics': topics,
                               'form': form})


@login_required
def edit(request, proposalid):
    proposal = Proposal.objects.get(id=proposalid)
    if (((proposal.proposer != request.user) or proposal.status in ['A', 'S'])
        and not topiclead(request.user, proposal.topic)):
        return forbidden()
    if request.method == 'POST':
        form = ProposalEditForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/%s' % request.session['lastlist'])
    else:
        form = ProposalEditForm(instance=proposal)
    return render_to_response('cfpedit.html',
                              {'req': request,
                               'form': form,
                               'proposal': proposal})


@login_required
def delete(request, proposalid):
    proposal = Proposal.objects.get(id=proposalid)
    if ((proposal.proposer != request.user) or proposal.status in ['A', 'S']):
        return forbidden()
    if request.method == 'POST':
        proposal.delete()
        return HttpResponseRedirect('/%s' % request.session['lastlist'])
    return render_to_response('cfpdelete.html',
                              {'req': request,
                               'proposal': proposal})


@login_required
def switch(request, proposalid):
    proposal = Proposal.objects.get(id=proposalid)
    if ((proposal.proposer != request.user)
      and not topiclead(request.user, proposal.topic)) or proposal.scheduled:
        return forbidden()
    if request.method == 'POST':
        form = ProposalSwitchForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            proposal = Proposal.objects.get(id=proposalid)
            proposal.status = 'U'
            proposal.save()
            return HttpResponseRedirect('/%s' % request.session['lastlist'])
    else:
        form = ProposalSwitchForm(instance=proposal)
    return render_to_response('cfpswitch.html',
                              {'req': request,
                               'form': form,
                               'proposal': proposal})


@login_required
def review(request, proposalid):
    proposal = Proposal.objects.get(id=proposalid)
    if not topiclead(request.user, proposal.topic):
        return forbidden()
    current_status = proposal.status
    status_long = proposal.get_status_display()
    if request.method == 'POST':
        form = ProposalReviewForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            if (settings.SEND_MAIL and current_status != proposal.status):
                lead = User.objects.get(username=proposal.topic.lead_username)
                if (lead.email and proposal.proposer.email):
                    message = """
This is an automated email.
If needed, you should reply directly to the topic lead (%s).

On your session proposal: %s
The topic lead (%s) changed status from %s to %s.

Reviewer's notes:
%s

You can edit your proposal at: %s/cfp/edit/%s""" \
                        % (proposal.topic.lead_username,
                           smart_str(proposal.title),
                           proposal.topic.lead_username,
                           status_long, proposal.get_status_display(),
                           smart_str(proposal.reviewer_notes),
                           settings.SITE_ROOT, proposalid)
                email = EmailMessage(settings.EMAIL_PREFIX +
                         "Status change on your session proposal",
                         message, settings.EMAIL_FROM,
                         [proposal.proposer.email, ], [],
                         headers={'Reply-To': lead.email})
                email.send()
            return HttpResponseRedirect('/cfp/topic/%d' % proposal.topic.id)
    else:
        form = ProposalReviewForm(instance=proposal)
    return render_to_response('cfpreview.html',
                              {'req': request,
                               'form': form,
                               'proposal': proposal,
                               'blueprints': linkify(proposal.blueprints)})


def dologout(request):
    logout(request)
    return HttpResponseRedirect('/')