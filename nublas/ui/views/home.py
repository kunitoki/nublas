import json
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.base import View, TemplateView

from taggit.models import Tag

from ...conf import settings
from ...models import Contact
from ..skins import get_skin_relative_path

import logging
logger = logging.getLogger(__name__)

__all__ = [ "Custom403View", "Custom404View", "Custom500View",
            "HomeView", "DashboardView", "TagsAutoCompleteView" ]


#==============================================================================
def Custom403View(request):
    return render_to_response(get_skin_relative_path('403.html'),
                              RequestContext(request, { }))

def Custom404View(request):
    print "xxxxx"
    return render_to_response(get_skin_relative_path('404.html'),
                              RequestContext(request, { }))

def Custom500View(request):
    return render_to_response(get_skin_relative_path('500.html'),
                              RequestContext(request, { }))


#==============================================================================
class HomeView(TemplateView):
    template_name = get_skin_relative_path("views/home/index.html")


#==============================================================================
class DashboardView(View):
    #@method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        # wrong configuration ?
        #if request.user.constraint_value("max_associations") == 0:
        #    messages.error(request, _('Something is wrong in your configuration. Please contact the administrator.'))
        #    return HttpResponseRedirect(reverse('backend:home'))

        # if no associations then redirect to add a first association
        #if not Association.objects.filter(Q(holder=request.user)).exists():
        #    messages.info(request, _('You need to create an association to continue.'))
        #    return HttpResponseRedirect(reverse('association:add'))

        # query data for the dashboard
        filter_contacts = Q(association__holder=request.user) | Q(association__collaborators=request.user)
        latest_contacts = Contact.objects.filter(filter_contacts).order_by("-_created")

        return render_to_response(get_skin_relative_path('views/dashboard/index.html'),
                                  RequestContext(request, { 'latest_contacts': latest_contacts }))


#==============================================================================
# TODO - use cache_page with at least a 30 min cache
class TagsAutoCompleteView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        result = []
        searchtext = request.GET['term']
        if len(searchtext) >= 2:
            tags = Tag.objects.filter(name__icontains=searchtext).order_by('name')[:10]
            for t in tags:
                result.append({ 'id': t.pk, 'label': str(t.name), 'value': str(t.name) }) # TODO - handle uuid ?

        return HttpResponse(json.dumps(result))
