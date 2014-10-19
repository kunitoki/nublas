import re
import csv
import os
import string
import mimetypes
from django import forms
from django.db import transaction
from django.db.models import Q
from django.conf import settings
#from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic.base import View

from ..files import GenericFileServeView
from ..skins import get_skin_relative_path
from ..forms import BaseForm, BaseModelForm # , CustomFieldModelForm
from ..widgets import TagsWidget
from ..search import SearchForm, search_contacts, search_events
from ...conf import settings
from ...models import Association, Contact, Event
from ...storages import private_storage
#    CustomQ, ContentTypeCustomField, ContentTypeCustomFieldValue, VALID_CUSTOM_CONTENT_TYPES

import logging
logger = logging.getLogger(__name__)

__all__ = [ "AssociationAddView", "AssociationAgendaLatestView",
            "AssociationAgendaView", "AssociationContactListActionView",
            "AssociationContactListView", "AssociationDeleteView",
            "AssociationDetailsView", "AssociationEditView",
            "AssociationFilesView", "AssociationFileServeView",
            "AssociationListView", "AssociationSettingsView" ]


#==============================================================================
class AssociationDetailsForm(BaseModelForm):
    class Meta:
        model = Association
        exclude = ('owner',
                   'collaborators',)
        widgets = {
            'tags': TagsWidget,
        }


#class AssociationCustomFieldsForm(CustomFieldModelForm):
#    class Meta:
#        model = Association
#        exclude = ('tags',)


class AssociationContactActionForm(BaseForm):
    contact_action = forms.CharField(required=True)


#==============================================================================
class AssociationListView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        user_filter = Q(owner=request.user) | Q(collaborators=request.user)

        # redirect if max_associations == 1
        #max_associations = request.user.constraint_value('max_associations')
        #if max_associations == 1:
        #    associations = Association.objects.filter(user_filter)
        #    if len(associations) == 1:
        #        return HttpResponseRedirect(reverse('nublas:association_details', args=[associations[0].uuid]))
        #    else:
        #        messages.info(request, _('You need to create an association to continue.'))
        #        return HttpResponseRedirect(reverse('nublas:association_add', args=[]))

        # real search
        search_query = user_filter
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                search_tokens = re.findall('\w+', form.cleaned_data['search'])
                for token in search_tokens:
                    search_query = search_query & Q(name__icontains=token)
        else:
            form = SearchForm()
        associations = Association.objects.filter(search_query)

        # special case for free newly registered users
        if len(associations) == 0:
            #if max_associations == 0:
            #    messages.error(request, _('Something went wrong with your configuration. Plase contact administrators.'))
            #else:
            messages.info(request, _('You need to create an association to continue.'))
            return HttpResponseRedirect(reverse('nublas:association_add', args=[]))

        return render_to_response(get_skin_relative_path('views/association/list.html'),
            RequestContext(request, { 'form': form,
                                      'associations': associations.distinct() }))


#==============================================================================
class AssociationDetailsView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        details_form = AssociationDetailsForm(instance=a)
        details_form.set_readonly(True)
        #custom_form = AssociationCustomFieldsForm(instance=a, association=a)
        #custom_form.set_readonly(True)

        return render_to_response(get_skin_relative_path('views/association/details.html'),
            RequestContext(request, { 'association': a,
                                      'details_form': details_form,
                                      #'custom_form': custom_form,
                                    }))


#==============================================================================
class AssociationEditView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        if request.method == 'POST':
            details_form = AssociationDetailsForm(request.POST, instance=a)
            #custom_form = AssociationCustomFieldsForm(request.POST, instance=a, association=a)
            if details_form.is_valid(): # and custom_form.is_valid()
                # save the forms
                details_form.save()
                #custom_form.save()
                # message the user and redirect to view
                messages.success(request, _('Association saved successfully.'))
                return HttpResponseRedirect(reverse('nublas:association_details', args=[a.uuid]))
            else:
                # forms are invalid
                logger.debug(details_form.errors)
                #logger.debug(custom_form.errors)
                messages.error(request, _('Cannot save the association.'))
        else:
            details_form = AssociationDetailsForm(instance=a)
            #custom_form = AssociationCustomFieldsForm(instance=a, association=a)

        return render_to_response(get_skin_relative_path('views/association/details.html'),
            RequestContext(request, { 'association': a,
                                      'details_form': details_form,
                                      #'custom_form': custom_form,
                                      'editing': True }))


#==============================================================================
class AssociationAddView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):

        # TODO - check this (rewrite)
        #if not request.user.check_constraint("max_associations", Association.objects.filter(owner=request.user).count() + 1):
        #    messages.error(request, _('You can not create more associations.'))
        #    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        if request.method == 'POST':
            a = Association(owner=request.user)
            details_form = AssociationDetailsForm(request.POST, instance=a)
            if details_form.is_valid():
                # save the forms
                details_form.save()
                # message the user and redirect to view
                messages.success(request, _('Association created successfully.'))
                return HttpResponseRedirect(reverse('nublas:association_details', args=[a.uuid]))
            else:
                # forms are invalid
                logger.debug(details_form.errors)
                messages.error(request, _('Cannot save the association.'))
        else:
            details_form = AssociationDetailsForm()

        return render_to_response(get_skin_relative_path('views/association/details.html'),
            RequestContext(request, { 'details_form': details_form,
                                      'editing': True,
                                      'adding': True }))


#==============================================================================
class AssociationDeleteView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        if request.method == 'POST':
            a.delete()
            messages.success(request, _('Association deleted successfully.'))
        else:
            messages.error(request, _('Cannot delete the association.'))

        return HttpResponseRedirect(reverse('nublas:association_list', args=[]))


#==============================================================================
class AssociationContactListView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        contacts = Contact.objects.filter(association=a)
        valid, searchtext, letter, contacts = search_contacts(request, contacts, a)
        contacts = contacts.distinct()

        paginator = Paginator(contacts, 50, allow_empty_first_page=True) # TODO - make user parametric

        if request.method == "POST":
            page = request.POST.get('page')
            try:
                contacts = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)
        else:
            contacts = paginator.page(1)

        return render_to_response(get_skin_relative_path('views/association/contacts.html'),
            RequestContext(request, { 'association': a,
                                      'searchtext': searchtext,
                                      'letter': letter,
                                      'contacts': contacts }))


#==============================================================================
class AssociationContactListActionView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        if request.method == 'POST':
            form = AssociationContactActionForm(request.POST)
            if form.is_valid():
                contact_action = str(form.cleaned_data['contact_action'])
                contact_list_selected = request.POST.getlist('contact_list_selected')
                if contact_list_selected is None:
                    contact_list_selected = []
                    if request.POST.get('contact_list_selected') is not None:
                        contact_list_selected = [request.POST.get('contact_list_selected')]
                if contact_list_selected is not None and len(contact_list_selected) > 0:
                    count = 0
                    if contact_action == "delete":
                        # delete selected contacts
                        for c in contact_list_selected:
                            try:
                                Contact.objects.get(association=a, _uuid=c).delete()
                                count += 1
                            except:
                                pass
                    elif contact_action == "export":
                        # export selected contacts as csv
                        field_names = set([field.name for field in Contact._meta.fields])
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(Contact._meta).replace('.', '_')
                        writer = csv.writer(response)
                        writer.writerow([unicode(field).encode('utf-8') for field in field_names])
                        for obj in Contact.objects.filter(association=a, _uuid__in=contact_list_selected):
                            writer.writerow([unicode(getattr(obj, field)).encode('utf-8') for field in field_names])
                            count += 1
                        return response
                    elif contact_action == "create_event":
                        logger.debug(contact_list_selected)
                        ## create an event with the selected contacts
                        #url = "%s?contacts=%s" % (reverse('nublas:agenda_event_add', args=[a.uuid]), ",".join(contact_list_selected))
                        #return HttpResponseRedirect(url)
                    elif contact_action == "merge":
                        # TODO merge selected views
                        pass
                    messages.success(request, \
                        _('Action executed successfully on %(count)s of %(total)s contacts.' % ({ 'count': count,
                                                                                                  'total': len(contact_list_selected)})))
                else:
                    messages.error(request, _('Error executing the selected action on an empty set.'))
            else:
                # TODO - rewrite it better
                logger.debug(form.errors)
                messages.error(request, _('Error executing the selected action.'))
        else:
            messages.error(request, _('Cannot execute the selected action.'))

        return HttpResponseRedirect(reverse('nublas:association_contacts', args=[a.uuid]))


#==============================================================================
class AssociationFilesView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        return render_to_response(get_skin_relative_path('views/association/files.html'),
            RequestContext(request, { 'association': a }))


#==============================================================================
class AssociationFileServeView(GenericFileServeView):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        return self.handle_request(request, a)


# #==============================================================================
# class AssociationCustomFieldForm(BaseModelForm):
#     def __init__(self, *args, **kwargs):
#         if kwargs.has_key('user'):
#             self.user = kwargs.pop('user')
#         if kwargs.has_key('association'):
#             self.association = kwargs.pop('association')
#         super(AssociationCustomFieldForm, self).__init__(*args, **kwargs)
#         # limit content_type to what user can do (constraint)
#         if self.user:
#             query = VALID_CUSTOM_CONTENT_TYPES.copy()
#             if self.user.check_constraint('has_app_dogs', 1):
#                 query['name__in'] = filter (lambda n: n != 'dog', query['name__in'])
#             self.fields['content_type'].queryset = ContentType.objects.filter(**query)
#         # TODO - remove validator (this can be useful in the future) !
#         del self.fields['validator']
#
#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if name: name = name.lower()
#         return name
#
#     def clean_data_type(self):
#         data_type = self.cleaned_data.get('data_type')
#         if self.instance and self.instance.data_type != data_type and self.association:
#             values_count = ContentTypeCustomFieldValue.objects.filter(association=self.association,
#                                                                       custom_field=self.instance).count()
#             if values_count > 0:
#                 raise forms.ValidationError(_("Cannot change the field datatype, some values already using '%(data_type)s'.") % {'data_type': self.instance.data_type})
#         return data_type
#
#     class Meta:
#         model = ContentTypeCustomField
#         exclude = ('association',
#                    'tags',)
#
#
# class BaseAssociationCustomView(View):
#     def message_errors(self, request, form_instance, error_text):
#         errors = form_instance.errors.get('__all__', [])
#         if len(errors) > 0:
#             for e in errors:
#                 messages.add_message(request, messages.ERROR, e)
#         else:
#             messages.add_message(request, messages.ERROR, error_text)
#
#
# class AssociationCustomView(View):
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         association = kwargs.get('association')
#
#         a = Association.get_object_or_404(association, request.user)
#
#         return render_to_response('base/association/custom.html',
#             RequestContext(request, { 'association': a }))
#
#
# class AssociationCustomAddView(BaseAssociationCustomView):
#     @method_decorator(login_required)
#     @method_decorator(transaction.commit_on_success)
#     def dispatch(self, request, *args, **kwargs):
#         association = kwargs.get('association')
#
#         a = Association.get_object_or_404(association, request.user)
#
#         if request.method == 'POST':
#             obj = ContentTypeCustomField(association=a)
#             inline_form = AssociationCustomFieldForm(request.POST, instance=obj, user=request.user, association=a)
#             if inline_form.is_valid():
#                 inline_form.save()
#                 # message the user and redirect to view
#                 messages.success(request, _('Custom field added successfully.'))
#                 return HttpResponseRedirect(reverse('association:custom', args=[a.uuid]))
#             else:
#                 self.message_errors(request, inline_form, _('Error adding custom field.'))
#         else:
#             inline_form = AssociationCustomFieldForm(user=request.user, association=a)
#
#         return render_to_response('base/association/custom/inline_view.html',
#             RequestContext(request, { 'inline_form': inline_form,
#                                       'title': _('Add custom field for '),
#                                       'object_name': a.name,
#                                       'section_title': _('Custom field data'),
#                                       'section_icon': 'iSignPost',
#                                       'back_url': reverse('association:custom', args=[a.uuid]),
#                                       'back_text': _('< Back to Association'),
#                                       'save_title': _('Save data'),
#                                       'submit_text': _('Create new custom field'),
#                                       'editing': True,
#                                       'adding': True }))
#
#
# class AssociationCustomEditView(BaseAssociationCustomView):
#     @method_decorator(login_required)
#     @method_decorator(transaction.commit_on_success)
#     def dispatch(self, request, *args, **kwargs):
#         obj = kwargs.get('object')
#
#         o = get_object_or_404(ContentTypeCustomField, _uuid=obj)
#         # TODO - check security
#         a = o.association
#
#         if request.method == 'POST':
#             inline_form = AssociationCustomFieldForm(request.POST, instance=o, association=a)
#             if inline_form.is_valid():
#                 inline_form.save()
#                 # message the user and redirect to view
#                 messages.success(request, _('Custom field modified successfully.'))
#                 return HttpResponseRedirect(reverse('association:custom', args=[a.uuid]))
#             else:
#                 self.message_errors(request, inline_form, _('Error saving custom field.'))
#         else:
#             inline_form = AssociationCustomFieldForm(instance=o, association=a)
#
#         return render_to_response('base/association/custom/inline_view.html',
#             RequestContext(request, { 'inline_form': inline_form,
#                                       'title': _('Edit custom field for '),
#                                       'object_name': a.name,
#                                       'section_title': _('Custom field data'),
#                                       'section_icon': 'iSignPost',
#                                       'back_url': reverse('association:custom', args=[a.uuid]),
#                                       'back_text': _('< Back to Association'),
#                                       'save_title': _('Save data'),
#                                       'submit_text': _('Save custom field'),
#                                       'editing': True }))
#
#
# class AssociationCustomDeleteView(View):
#     @method_decorator(login_required)
#     @method_decorator(transaction.commit_on_success)
#     def dispatch(self, request, *args, **kwargs):
#         obj = kwargs.get('object')
#
#         o = get_object_or_404(ContentTypeCustomField, _uuid=obj)
#         # TODO - check security
#         a = o.association
#
#         if request.method == 'POST':
#             o.delete()
#             # TODO - delete (trash) the values too
#             messages.success(request, _('Custom field deleted successfully.'))
#         else:
#             messages.error(request, _('Cannot delete the custom field.'))
#
#         return HttpResponseRedirect(reverse('association:custom', args=[a.uuid]))
#

#==============================================================================
class AssociationAgendaView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        events = Event.objects.filter(calendar__association=a)
        valid, searchtext, events = search_events(request, events, a)
        if searchtext == '':
            events = events.none()
        else:
            events = events.distinct()

        paginator = Paginator(events, 10, allow_empty_first_page=True) # Show 10 events per page

        if request.method == "POST":
            page = request.POST.get('page')
            try:
                events = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                events = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                events = paginator.page(paginator.num_pages)
        else:
            events = paginator.page(1)

        latest_events = Event.objects.filter(calendar__association=a) \
                             .filter(start_date__gte=timezone.now()) \
                             .exclude(end_date__lte=timezone.now()) \
                             .order_by('start_date')[:5]

        return render_to_response(get_skin_relative_path('views/association/agenda.html'),
            RequestContext(request, { 'association': a,
                                      'searchtext': searchtext,
                                      'events': events,
                                      'latest_events': latest_events }))


class AssociationAgendaLatestView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        latest_events = Event.objects.filter(calendar__association=a) \
                             .filter(start_date__gte=timezone.now()) \
                             .exclude(end_date__lte=timezone.now()) \
                             .order_by('start_date')[:5]

        return render_to_response(get_skin_relative_path('views/association/agenda/event_list.html'),
            RequestContext(request, { 'association': a,
                                      'latest_events': latest_events,
                                      'use_head': True }))


#==============================================================================
class AssociationSettingsView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        return render_to_response(get_skin_relative_path('views/association/settings.html'),
            RequestContext(request, { 'association': a }))
