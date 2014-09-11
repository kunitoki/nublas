from django.conf.urls import patterns, include, url
from django.template import RequestContext
from django.shortcuts import render_to_response


def home(request):
    return render_to_response("nublas/base.html",
                              {},
                              context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^$', home),
)
