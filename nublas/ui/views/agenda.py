import sys
import json
from django import forms
from django.db import transaction
from django.db.models import Q
#from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt

from ..skins import get_skin_relative_path
from ..widgets import DateTimeWidget, SelectWidget, AutoCompleteWidget
from ..forms import BaseForm, BaseModelForm
#from ..forms import CustomFieldModelForm
from ...conf import settings
from ...models import Association, Contact, ContactAppointment, Event, Calendar

import logging
logger = logging.getLogger(__name__)


#==============================================================================
class ListEventByDateForm(BaseForm):
    start = forms.DateTimeField(required=False) # input_formats=['%Y-%m-%d'],
    end = forms.DateTimeField(required=False) # input_formats=['%Y-%m-%d'],

    def update_instance(self, instance, commit=True):
        for f in instance._meta.fields:
            if f.attname in self.fields:
                setattr(instance, f.attname, self.cleaned_data[f.attname])
        if commit:
            try:
                instance.save()
            except:
                return False
        return instance

class PartialEventForm(BaseForm):
    start_date = forms.DateTimeField(required=True) # input_formats=['%Y-%m-%d %H:%M'],
    end_date = forms.DateTimeField(required=False) # input_formats=['%Y-%m-%d %H:%M'],
    allday = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(PartialEventForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if not end_date:
            cleaned_data.set("end_date", start_date)
        return cleaned_data

    def update_instance(self, instance, commit=True):
        for f in instance._meta.fields:
            if f.attname in self.fields:
                setattr(instance, f.attname, self.cleaned_data[f.attname])
        if commit:
            try:
                instance.save()
            except:
                logger.error(sys.exc_info())
                return False
        return instance


#==============================================================================
class AgendaAllEventListJsonView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        associations = Association.objects.filter(holder=request.user) # TODO - collaborators
        e = Event.objects.filter(calendar__association__in=associations)

        form = ListEventByDateForm(request.REQUEST)
        if form.is_valid():
            start_date = form.cleaned_data['start']
            if start_date:
                e = e.filter(start_date__gte=start_date)
            end_date = form.cleaned_data['end']
            if end_date:
                e = e.filter(end_date__lte=end_date)

        if not request.user.is_superuser:
            e = e.exclude(Q(calendar__public=False), ~Q(owner=request.user))
            # TODO - add collaborators

        events = []
        for event in e.order_by('start_date'):
            #context = {
            #    'title': event.title,
            #    'details': event.details,
            #    'contacts': event.contacts.count(),
            #    #'dogs': event.dogs.count(),
            #}
            events.append({
                'id': str(event.uuid),
                'title': event.title,
                'details': event.details,
                #'verbose': render_to_string('base/agenda/event_verbose.html', context),
                'start': event.start_date.strftime("%Y-%m-%d %H:%M:00 %Z"),
                'end': event.end_date.strftime("%Y-%m-%d %H:%M:00 %Z"),
                'className': 'fc-calendar-%s' % event.calendar.unique_identifier(),
                'allDay': event.allday,
                'editable': True,
                # TODO - what about permissions ?
            });

        response = HttpResponse(json.dumps(events), content_type='application/json')
        response['Pragma'] = 'no-cache'
        return response


#==============================================================================
class AgendaAllEventListCssView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        associations = Association.objects.filter(holder=request.user) # TODO - collaborators

        rendered = []
        calendar_list = Calendar.objects.filter(association__in=associations)
        for cal in calendar_list:
            rendered.append('''
                .fc-calendar-%(name)s, .fc-view .fc-calendar-%(name)s .fc-event-inner, .fc-calendar-%(name)s a {
                    background-color:%(colour)s; border-color:%(colour)s; color:white;
                }''' % {'name': cal.unique_identifier(), 'colour': cal.colour})

        response = HttpResponse('\n'.join(rendered), content_type='text/css')
        response['Pragma'] = 'no-cache'
        return response


#==============================================================================
class AgendaEventListJsonView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)
        e = Event.objects.filter(calendar__association=a)

        form = ListEventByDateForm(request.REQUEST)
        if form.is_valid():
            start_date = form.cleaned_data['start']
            if start_date:
                e = e.filter(start_date__gte=start_date)
            end_date = form.cleaned_data['end']
            if end_date:
                e = e.filter(end_date__lte=end_date)

        if not request.user.is_superuser:
            e = e.exclude(Q(calendar__public=False), ~Q(owner=request.user))
            # TODO - add collaborators

        events = []
        for event in e.order_by('start_date'):
            #context = {
            #    'title': event.title,
            #    'details': event.details,
            #    'contacts': event.contacts.count(),
            #    #'dogs': event.dogs.count(),
            #}
            events.append({
                'id': str(event.uuid),
                'title': event.title,
                'details': event.details,
                #'verbose': render_to_string('base/agenda/event_verbose.html', context),
                'start': event.start_date.strftime("%Y-%m-%d %H:%M:00 %Z"),
                'end': event.end_date.strftime("%Y-%m-%d %H:%M:00 %Z"),
                'className': 'fc-calendar-%s' % event.calendar.unique_identifier(),
                'allDay': event.allday,
                'editable': True,
                # TODO - what about permissions ?
            });

        response = HttpResponse(json.dumps(events), content_type='application/json')
        response['Pragma'] = 'no-cache'
        return response


#==============================================================================
class AgendaEventListCssView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        a = Association.get_object_or_404(association, request.user)

        rendered = []
        calendar_list = Calendar.objects.filter(association=a)
        for cal in calendar_list:
            rendered.append('''
                .fc-calendar-%(name)s, .fc-view .fc-calendar-%(name)s .fc-event-inner, .fc-calendar-%(name)s a {
                    background-color:%(colour)s; border-color:%(colour)s; color:white;
                }''' % {'name': cal.unique_identifier(), 'colour': cal.colour})

        response = HttpResponse('\n'.join(rendered), content_type='text/css')
        response['Pragma'] = 'no-cache'
        return response


#==============================================================================
class AgendaEventForm(BaseModelForm):
    start_date = forms.DateTimeField(input_formats=('%Y-%m-%d %H:%M',)),
    end_date = forms.DateTimeField(input_formats=('%Y-%m-%d %H:%M',)),

    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        super(AgendaEventForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['calendar'].queryset = Calendar.objects.filter(association=a)

    class Meta:
        model = Event
        exclude = ('owner',
                   'contacts',)
        widgets = {
            'calendar': SelectWidget,
            'start_date': DateTimeWidget,
            'end_date': DateTimeWidget,
        }


#class AgendaEventCustomFieldsForm(CustomFieldModelForm):
#    class Meta:
#        model = Event
#        exclude = ('tags',)


class AgendaEventContactAppointmentForm(BaseModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput())
    contact = forms.ModelChoiceField(queryset=Contact.objects.all())
    info = forms.CharField(widget=forms.TextInput(), required=False)
    attended = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(AgendaEventContactAppointmentForm, self).__init__(*args, **kwargs)
        #self.fields.insert(0, 'id', self.fields['id']) # HACK - keep id first field

    def clean_contact(self):
        value = self.cleaned_data['contact']
        print(value)
        return value

    #def clean_id(self):
    #    new_id = self.cleaned_data['id']
    #    print(new_id)
    #    try:
    #        return int(new_id)
    #    except ValueError:
    #        return None

    class Meta:
        model = ContactAppointment
        fields = ('id', 'contact', 'info', 'attended')


class AgendaEventContactAppointmentFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        super(AgendaEventContactAppointmentFormSet, self).__init__(*args, **kwargs)
        if a:
            autocomplete_url = reverse('nublas:contact_search_autocomplete', args=[a.uuid])
            for form in self.forms:
                if 'contact' in form.fields:
                    form.fields['contact'].queryset = Contact.objects.filter(association=a)
                    form.fields['contact'].widget = AutoCompleteWidget(url=autocomplete_url,
                                                                       model=Contact)
                form._update_widgets_error_state()


def custom_agenda_event_field_callback(field):
    return field.formfield()


#==============================================================================
class AgendaEventBaseView(View):
    def redirect_url(self, *args, **kwargs):
        return reverse('nublas:association_agenda', args=args)

    def object_name(self, obj):
        return '%s' % (obj.name)

    def message_errors(self, request, form_instance, error_text):
        def _get_form_errors(form):
            if isinstance(form, BaseInlineFormSet):
                err = []
                for frm in form.forms:
                    err += frm.errors.get('__all__', [])
                return err
            else:
                return form.errors.get('__all__', [])

        errors = []
        if isinstance(form_instance, list):
            for f in form_instance:
                errors += _get_form_errors(f)
        else:
            errors += _get_form_errors(form_instance)

        if len(errors) > 0:
            for e in errors:
                print e
                messages.add_message(request, messages.ERROR, e)
        else:
            messages.add_message(request, messages.ERROR, error_text)


#==============================================================================
class AgendaEventAddView(AgendaEventBaseView):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        # TODO - handle security
        a = Association.get_object_or_404(association, request.user)

        # initial precompiled contacts
        extra = 0
        initial = []

        contact = request.GET.get('contact', None)
        if contact:
            contacts = Contact.objects.filter(_uuid=contact)
            for c in contacts:
                initial.append({'contact': c})
                extra += 1

        contacts = request.GET.get('contacts', None)
        if contacts:
            contacts = Contact.objects.filter(_uuid__in=contacts.split(','))
            for c in contacts:
                initial.append({'contact': c})
                extra += 1

        # create the formset class
        contact_formset_class = inlineformset_factory(Event,
                                                      Event.contacts.through,
                                                      form=AgendaEventContactAppointmentForm,
                                                      formset=AgendaEventContactAppointmentFormSet,
                                                      can_delete=False,
                                                      extra=extra,
                                                      formfield_callback=custom_agenda_event_field_callback)

        if request.method == 'POST':
            o = Event(owner=request.user)
            inline_form = AgendaEventForm(request.POST, instance=o, association=a)
            #custom_form = AgendaEventCustomFieldsForm(request.POST, instance=o, association=a)
            contact_formset = contact_formset_class(request.POST,
                                                    request.FILES,
                                                    instance=o,
                                                    association=a,
                                                    initial=initial,
                                                    prefix='contacts')
            if inline_form.is_valid() and contact_formset.is_valid(): # and custom_form.is_valid()
                inline_form.save()
                #custom_form.save()
                contact_formset.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, _('Event created successfully.'))
                return HttpResponseRedirect(self.redirect_url(a.uuid))
            else:
                self.message_errors(request, [inline_form, contact_formset], _('Cannot save the event.'))
        else:
            inline_form = AgendaEventForm(initial=request.GET, association=a)
            #custom_form = AgendaEventCustomFieldsForm(association=a)
            contact_formset = contact_formset_class(association=a,
                                                    initial=initial,
                                                    prefix='contacts')

        return render_to_response(get_skin_relative_path('views/agenda/event_view.html'),
            RequestContext(request, { 'association': a,
                                      'inline_form': inline_form,
                                      #'custom_form': custom_form,
                                      'contact_formset': contact_formset,
                                      'title': _('Adding new event for '),
                                      'object_name': self.object_name(a),
                                      'section_title': _('Event data'),
                                      'section_icon': 'fa-calendar',
                                      'back_url': self.redirect_url(association),
                                      'back_text': _('< Back to Association'),
                                      'save_title': _('Save data'),
                                      'submit_text': _('Create new event'),
                                      'editing': True,
                                      'adding': True }))


#==============================================================================
class AgendaEventEditView(AgendaEventBaseView):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        obj = kwargs.get('object')

        o = get_object_or_404(Event, _uuid=obj)
        a = o.calendar.association

        contact_formset_class = inlineformset_factory(Event,
                                                      Event.contacts.through,
                                                      form=AgendaEventContactAppointmentForm,
                                                      formset=AgendaEventContactAppointmentFormSet,
                                                      can_delete=True,
                                                      extra=0,
                                                      fields=('contact', 'info', 'attended'),
                                                      formfield_callback=custom_agenda_event_field_callback)

        if request.method == 'POST':
            inline_form = AgendaEventForm(request.POST, instance=o, association=a)
            #custom_form = AgendaEventCustomFieldsForm(request.POST, instance=o, association=a)
            contact_formset = contact_formset_class(request.POST,
                                                    request.FILES,
                                                    instance=o,
                                                    association=a,
                                                    prefix='contacts')
            if inline_form.is_valid() and contact_formset.is_valid(): # and custom_form.is_valid()
                inline_form.save()
                #custom_form.save()
                contact_formset.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, _('Event saved successfully.'))
                return HttpResponseRedirect(self.redirect_url(a.uuid))
            else:
                self.message_errors(request, [inline_form, contact_formset], _('Cannot save the event.'))
        else:
            inline_form = AgendaEventForm(instance=o, association=a)
            #custom_form = AgendaEventCustomFieldsForm(instance=o, association=a)
            contact_formset = contact_formset_class(instance=o, association=a, prefix='contacts')

        return render_to_response(get_skin_relative_path('views/agenda/event_view.html'),
            RequestContext(request, { 'association': a,
                                      'inline_form': inline_form,
                                      #'custom_form': custom_form,
                                      'contact_formset': contact_formset,
                                      'title': _('Edit event for '),
                                      'object_name': self.object_name(a),
                                      'section_title': _('Event data'),
                                      'section_icon': 'fa-calendar',
                                      'back_url': self.redirect_url(a.uuid),
                                      'back_text': _('< Back to Association'),
                                      'save_title': _('Save data'),
                                      'submit_text': _('Save event'),
                                      'editing': True }))


#==============================================================================
class AgendaEventResizeView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt) # TODO - handle in a better way
    def dispatch(self, request, *args, **kwargs):
        obj = kwargs.get('object')

        event = get_object_or_404(Event, _uuid=obj)
        # TODO - handle security
        #a = event.calendar.association

        updateOk = False
        errors = {}

        try:
            form = PartialEventForm(request.REQUEST)
            if form.is_valid():
                form.update_instance(event)
                updateOk = True
            else:
                errors = form.errors
        except Event.DoesNotExist:
            errors['500'] = _('Event does not exists !')

        response_string = json.dumps({ 'result': updateOk, 'errors': errors });
        response = HttpResponse(response_string, content_type='application/json')
        return response


#==============================================================================
class AgendaEventDeleteView(AgendaEventBaseView):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        obj = kwargs.get('object')

        event = get_object_or_404(Event, _uuid=obj)
        # TODO - handle security
        a = event.calendar.association

        if request.method == 'POST':
            event.delete()
            messages.add_message(request, messages.SUCCESS, _('Event deleted successfully.'))
        else:
            messages.add_message(request, messages.ERROR, _('Cannot delete the event.'))

        return HttpResponseRedirect(self.redirect_url(a.uuid))
