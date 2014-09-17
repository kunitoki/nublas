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
from django.views.generic.base import View
from django.views.generic import TemplateView

from ...conf import settings
from ...models import Contact
from ..skins import get_skin_relative_path

import logging
logger = logging.getLogger(__name__)


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