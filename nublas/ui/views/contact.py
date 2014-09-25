import re
import json
import string
from django import forms
from django.db import transaction
from django.db.models import Q
#from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
#from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic.base import View

#from nublas.library.db.fields.autocomplete import AutoCompleteWidget
#from ..generic.fileserve import GenericFileServeView

from ..skins import get_skin_relative_path
from ..forms import BaseForm, BaseModelForm # , CustomFieldModelForm
from ..search import SearchForm, search_contacts
from ...conf import settings
from ...models import (Association, Contact, Group, ContactGroup,
    Address, Phone, Email, Website, Subscription, Relationship,
    PrefixType, SuffixType, ContactType, GenderType, AddressType, PhoneType,
    PhoneKind, EmailType, WebsiteType, SubscriptionType, RelationshipType)

import logging
logger = logging.getLogger(__name__)

__all__ = [ "ContactListView", "ContactAddView", "ContactDetailsView",
            "ContactDeleteView", "ContactEditView", "ContactAddressAddView",
            "ContactAddressDeleteView", "ContactAddressEditView",
            "ContactAutoCompleteView", "ContactEmailAddView",
            "ContactEmailDeleteView", "ContactEmailEditView",
            "ContactFilesView", "ContactGroupView", "ContactGroupAddView",
            "ContactGroupDeleteView", "ContactGroupEditView",
            "ContactPartecipationView", "ContactPhoneAddView",
            "ContactPhoneDeleteView", "ContactPhoneEditView",
            "ContactRelationshipAddView", "ContactRelationshipDeleteView",
            "ContactRelationshipEditView", "ContactRelationshipView",
            "ContactSubscriptionAddView", "ContactSubscriptionDeleteView",
            "ContactSubscriptionEditView", "ContactSubscriptionView",
            "ContactWebsiteAddView", "ContactWebsiteDeleteView",
            "ContactWebsiteEditView" ]


#==============================================================================
class GenericContactInlineView(View):
    def __init__(self):
        self.cls = None
        self.contact_fieldname = 'contact'
        self.form = None
        self.custom_form = None
        self.name = None
        self.title = None
        self.section_title = None
        self.section_icon = None
        self.back_text = _('Back to Contact')
        self.submit_text = None
        self.success_text = None
        self.error_text = None
        super(GenericContactInlineView, self).__init__()

    def message_errors(self, request, form_instance, error_text):
        errors = form_instance.errors.get('__all__', [])
        if len(errors) > 0:
            for e in errors:
                messages.add_message(request, messages.ERROR, e)
        else:
            messages.add_message(request, messages.ERROR, error_text)

    def check_is_valid(self, *args):
        all_passed = True
        for f in args:
            if f and not f.is_valid():
                all_passed = False
                break
        return all_passed

    def redirect_url(self, *args):
        return None

    def object_name(self, obj):
        return None


class GenericContactInlineAddView(GenericContactInlineView):
    def redirect_url(self, *args):
        return reverse('nublas:contact_edit', args=args)

    def object_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        custom_form = None

        if request.method == 'POST':
            o = self.cls(**{ self.contact_fieldname: c })
            inline_form = self.form(request.POST, instance=o, association=a, contact=c)
            if self.custom_form:
                custom_form = self.custom_form(request.POST, instance=o, association=a)
            if self.check_is_valid(inline_form, custom_form, tags_form):
                inline_form.save() # must be saved first
                if custom_form:
                    custom_form.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, self.success_text)
                return HttpResponseRedirect(self.redirect_url(c.uuid))
            else:
                # forms are invalid
                self.message_errors(request, inline_form, self.error_text)
        else:
            inline_form = self.form(association=a, contact=c)
            if self.custom_form:
                custom_form = self.custom_form(association=a)

        return render_to_response(get_skin_relative_path('generic/inline_view.html'),
            RequestContext(request, { 'inline_form': inline_form,
                                      'custom_form': custom_form,
                                      'title': self.title,
                                      'object_name': self.object_name(c),
                                      'section_title': self.section_title,
                                      'section_icon': self.section_icon,
                                      'back_url': self.redirect_url(c.uuid),
                                      'back_text': self.back_text,
                                      'save_title': _('Save data'),
                                      'submit_text': self.submit_text,
                                      'editing': True,
                                      'adding': True }))


class GenericContactInlineEditView(GenericContactInlineView):
    def redirect_url(self, *args):
        return reverse('nublas:contact_edit', args=args)

    def object_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        obj = kwargs.get('object')

        o = get_object_or_404(self.cls, _uuid=obj)
        # TODO - check security
        c = getattr(o, self.contact_fieldname, None)
        a = c.association

        custom_form = None

        if request.method == 'POST':
            inline_form = self.form(request.POST, instance=o, association=a, contact=c)
            if self.custom_form:
                custom_form = self.custom_form(request.POST, instance=o, association=a)
            if self.check_is_valid(inline_form, custom_form, tags_form):
                inline_form.save() # must be saved first
                if custom_form: custom_form.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, self.success_text)
                return HttpResponseRedirect(self.redirect_url(c.uuid))
            else:
                # forms are invalid
                self.message_errors(request, inline_form, self.error_text)
        else:
            inline_form = self.form(instance=o, association=a, contact=c)
            if self.custom_form:
                custom_form = self.custom_form(instance=o, association=a)

        return render_to_response(get_skin_relative_path('generic/inline_view.html'),
            RequestContext(request, { 'inline_form': inline_form,
                                      'custom_form': custom_form,
                                      'title': self.title,
                                      'object_name': self.object_name(c),
                                      'section_title': self.section_title,
                                      'section_icon': self.section_icon,
                                      'back_url': self.redirect_url(c.uuid),
                                      'back_text': self.back_text,
                                      'save_title': _('Save data'),
                                      'submit_text': self.submit_text,
                                      'editing': True }))


class GenericContactInlineDeleteView(GenericContactInlineView):
    def redirect_url(self, *args):
        return reverse('nublas:contact_edit', args=args)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        obj = kwargs.get('object')

        o = get_object_or_404(self.cls, _uuid=obj)
        # TODO - check security
        c = getattr(o, self.contact_fieldname, None)
        #a = c.association

        if request.method == 'POST':
            o.delete()
            messages.add_message(request, messages.SUCCESS, self.success_text)
        else:
            messages.add_message(request, messages.ERROR, self.error_text)

        return HttpResponseRedirect(self.redirect_url(c.uuid))


#==============================================================================
class ContactPersonalForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        super(ContactPersonalForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['prefix'].queryset = PrefixType.objects.filter(association=a)
            self.fields['suffix'].queryset = SuffixType.objects.filter(association=a)
            self.fields['type'].queryset = ContactType.objects.filter(association=a)
            self.fields['gender'].queryset = GenderType.objects.filter(association=a)

    class Meta:
        model = Contact
        fieldsets = (
            (None, {
                'fields': (
                    ('first_name', 'middle_name', 'last_name'),
                    ('nickname', 'prefix', 'suffix'),
                    ('type', 'is_enabled'),
                    'gender',
                    'birth_date',
                    ('decease_date', 'is_deceased'),
                    ('do_not_contact', 'do_not_call', 'do_not_sms', 'do_not_mail'),
                    'notes',
                    'tags',
                )
            }),
        )
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5}),
        }
        exclude = ('association',
                   'groups',)

#class ContactCustomFieldsForm(CustomFieldModelForm):
#    class Meta:
#        model = Contact
#        exclude = ('tags',)


#==============================================================================
class ContactListView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        # TODO - check security
        a = Association.get_object_or_404(association, request.user)

        contacts = Contact.objects.filter(association=a)
        valid_search, contacts = search_contacts(request, contacts)

        # TODO - copy from association

        return render_to_response(get_skin_relative_path('views/contact/list.html'),
            RequestContext(request, { 'association': a,
                                      'contacts': contacts.distinct() }))


#==============================================================================
class ContactDetailsView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact.objects.select_related(), _uuid=contact)
        # TODO - check security
        a = c.association

        personal_form = ContactPersonalForm(instance=c, association=a)
        personal_form.set_readonly(True)
        #custom_form = ContactCustomFieldsForm(instance=c, association=a)
        #custom_form.set_readonly(True)

        return render_to_response(get_skin_relative_path('views/contact/details.html'),
            RequestContext(request, { 'personal_form': personal_form,
                                      #'custom_form': custom_form,
                                      'association': a,
                                      'contact': c }))


#==============================================================================
class ContactEditView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        if request.method == 'POST':
            personal_form = ContactPersonalForm(request.POST, instance=c, association=a)
            #custom_form = ContactCustomFieldsForm(request.POST, instance=c, association=a)
            if personal_form.is_valid(): # and custom_form.is_valid()
                # save the forms
                personal_form.save()
                #custom_form.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, _('Contact saved successfully.'))
                return HttpResponseRedirect(reverse('nublas:contact_details', args=[c.uuid]))
            else:
                # forms are invalid
                messages.add_message(request, messages.ERROR, _('Cannot save the contact.'))
        else:
            personal_form = ContactPersonalForm(instance=c, association=a)
            #custom_form = ContactCustomFieldsForm(instance=c, association=a)

        return render_to_response(get_skin_relative_path('views/contact/details.html'),
            RequestContext(request, { 'personal_form': personal_form,
                                      #'custom_form': custom_form,
                                      'association': a,
                                      'contact': c,
                                      'editing': True }))


#==============================================================================
class ContactAddView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        # TODO - permission denied
        a = Association.get_object_or_404(association, request.user)

        if request.method == 'POST':
            c = Contact(association=a)
            personal_form = ContactPersonalForm(request.POST, instance=c, association=a)
            #custom_form = ContactCustomFieldsForm(request.POST, instance=c, association=a)
            if personal_form.is_valid(): # and custom_form.is_valid()
                # save the forms
                personal_form.save()
                #custom_form.save()
                # message the user and redirect to view
                messages.add_message(request, messages.SUCCESS, _('Contact created successfully.'))
                return HttpResponseRedirect(reverse('nublas:contact_details', args=[c.uuid]))
            else:
                # forms are invalid
                messages.add_message(request, messages.ERROR, _('Cannot save the contact.'))
        else:
            personal_form = ContactPersonalForm(association=a)
            #custom_form = ContactCustomFieldsForm(association=a)

        return render_to_response(get_skin_relative_path('views/contact/details.html'),
            RequestContext(request, { 'personal_form': personal_form,
                                      #'custom_form': custom_form,
                                      'association': a,
                                      'editing': True,
                                      'adding': True }))


#==============================================================================
class ContactDeleteView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        if request.method == 'POST':
            c.delete()
            messages.add_message(request, messages.SUCCESS, _('Contact deleted successfully.'))
        else:
            messages.add_message(request, messages.ERROR, _('Cannot delete the contact.'))

        return HttpResponseRedirect(reverse('nublas:association_contacts', args=[a.uuid]))


#==============================================================================
class ContactFilesView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        return render_to_response('base/contact/files.html',
            RequestContext(request, { 'association': a,
                                      'contact': c }))


#==============================================================================
#class ContactFileServeView(GenericFileServeView):
#    def get_opts(self, request, **kwargs):
#        contact = kwargs.get('contact')
#
#        c = get_object_or_404(Contact, _uuid=contact)
#        # TODO - check security
#        a = c.association
#
#        # get root
#        root_path = c.get_documents_path()
#
#        # available space
#        freespace = request.user.constraint_value('max_diskspace') - a.get_documents_disksize()
#        max_size = min(freespace, settings.FILE_UPLOAD_MAX_MEMORY_SIZE) / (1024 * 1024)
#
#        # return connector options
#        return {
#            'root': root_path,
#            'uploadMaxSize': max_size,
#            'diskspaceMaxSize': max_size,
#        }


#==============================================================================
class AddressForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(AddressForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = AddressType.objects.filter(association=a)

    class Meta:
        model = Address
        fieldsets = (
            (None, {
                'fields': (
                    ('type', 'is_main'),
                    'address',
                    ('city', 'cap'),
                    'country',
                    'is_billing'
                ),
                'layout': (
                    (5, 2),
                    10,
                    (4, 5),
                    4,
                    2
                ),
            }),
        )
        exclude = ('contact',
                   'tags',)


class ContactAddressAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactAddressAddView, self).__init__()
        self.cls = Address
        self.form = AddressForm
        self.title = _('Adding new address for ')
        self.section_title = _('Address data')
        self.section_icon = 'fa-flag'
        self.submit_text = _('Create new address')
        self.success_text = _('Address created successfully.')
        self.error_text = _('Cannot save the address.')


class ContactAddressEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactAddressEditView, self).__init__()
        self.cls = Address
        self.form = AddressForm
        self.title = _('Editing address for ')
        self.section_title = _('Address data')
        self.section_icon = 'fa-flag'
        self.submit_text = _('Save address')
        self.success_text = _('Address modified successfully.')
        self.error_text = _('Cannot save the address.')


class ContactAddressDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactAddressDeleteView, self).__init__()
        self.cls = Address
        self.success_text = _('Address deleted successfully.')
        self.error_text = _('Cannot delete the address.')


#==============================================================================
class PhoneForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(PhoneForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = PhoneType.objects.filter(association=a)
            self.fields['kind'].queryset = PhoneKind.objects.filter(association=a)

    class Meta:
        model = Phone
        exclude = ('contact',
                   'tags',)


class ContactPhoneAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactPhoneAddView, self).__init__()
        self.cls = Phone
        self.form = PhoneForm
        self.title = _('Adding new phone for ')
        self.section_title = _('Phone data')
        self.section_icon = 'fa-phone'
        self.submit_text = _('Create new phone')
        self.success_text = _('Phone created successfully.')
        self.error_text = _('Cannot save the phone.')


class ContactPhoneEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactPhoneEditView, self).__init__()
        self.cls = Phone
        self.form = PhoneForm
        self.title = _('Editing phone for ')
        self.section_title = _('Phone data')
        self.section_icon = 'fa-phone'
        self.submit_text = _('Save phone')
        self.success_text = _('Phone modified successfully.')
        self.error_text = _('Cannot save the phone.')


class ContactPhoneDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactPhoneDeleteView, self).__init__()
        self.cls = Phone
        self.success_text = _('Phone deleted successfully.')
        self.error_text = _('Cannot delete the phone.')


#==============================================================================
class EmailForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(EmailForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = EmailType.objects.filter(association=a)

    class Meta:
        model = Email
        exclude = ('contact',
                   'tags',)


class ContactEmailAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactEmailAddView, self).__init__()
        self.cls = Email
        self.form = EmailForm
        self.title = _('Adding new email for ')
        self.section_title = _('Email data')
        self.section_icon = 'fa-envelope'
        self.submit_text = _('Create new email')
        self.success_text = _('Email created successfully.')
        self.error_text = _('Cannot save the email.')


class ContactEmailEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactEmailEditView, self).__init__()
        self.cls = Email
        self.form = EmailForm
        self.title = _('Editing email for ')
        self.section_title = _('Email data')
        self.section_icon = 'fa-envelope'
        self.submit_text = _('Save email')
        self.success_text = _('Email modified successfully.')
        self.error_text = _('Cannot save the email.')


class ContactEmailDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactEmailDeleteView, self).__init__()
        self.cls = Email
        self.success_text = _('Email deleted successfully.')
        self.error_text = _('Cannot delete the email.')


#==============================================================================
class WebsiteForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(WebsiteForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = WebsiteType.objects.filter(association=a)

    class Meta:
        model = Website
        exclude = ('contact',
                   'tags',)


class ContactWebsiteAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactWebsiteAddView, self).__init__()
        self.cls = Website
        self.form = WebsiteForm
        self.title = _('Adding new website for ')
        self.section_title = _('Website data')
        self.section_icon = 'fa-globe'
        self.submit_text = _('Create new website')
        self.success_text = _('Website created successfully.')
        self.error_text = _('Cannot save the website.')


class ContactWebsiteEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactWebsiteEditView, self).__init__()
        self.cls = Website
        self.form = WebsiteForm
        self.title = _('Editing website for ')
        self.section_title = _('Website data')
        self.section_icon = 'fa-globe'
        self.submit_text = _('Save website')
        self.success_text = _('Website modified successfully.')
        self.error_text = _('Cannot save the website.')


class ContactWebsiteDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactWebsiteDeleteView, self).__init__()
        self.cls = Website
        self.success_text = _('Website deleted successfully.')
        self.error_text = _('Cannot delete the website.')


#==============================================================================
class ContactGroupForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(ContactGroupForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['group'].queryset = Group.objects.filter(association=a)

    class Meta:
        model = ContactGroup
        exclude = ('contact',
                   'tags',)


class ContactGroupView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        return render_to_response(get_skin_relative_path('views/contact/groups.html'),
            RequestContext(request, { 'association': a,
                                      'contact': c }))


class ContactGroupAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactGroupAddView, self).__init__()
        self.cls = ContactGroup
        self.form = ContactGroupForm
        self.title = _('Assigning new group to ')
        self.section_title = _('Group data')
        self.section_icon = 'fa-users'
        self.submit_text = _('Assign group')
        self.success_text = _('Group assigned successfully.')
        self.error_text = _('Cannot assign the group.')


class ContactGroupEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactGroupEditView, self).__init__()
        self.cls = ContactGroup
        self.form = ContactGroupForm
        self.title = _('Editing a group assignment for ')
        self.section_title = _('Group assignment data')
        self.section_icon = 'fa-users'
        self.submit_text = _('Save group assignment')
        self.success_text = _('Group assignment modified successfully.')
        self.error_text = _('Cannot save the group assignment.')


class ContactGroupDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactGroupDeleteView, self).__init__()
        self.cls = ContactGroup
        self.success_text = _('Group unassigned successfully.')
        self.error_text = _('Cannot unassign the group.')


#==============================================================================
class SubscriptionForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = SubscriptionType.objects.filter(association=a)

    class Meta:
        model = Subscription
        exclude = ('contact',)


#class SubscriptionCustomFieldsForm(CustomFieldModelForm):
#    class Meta:
#        model = Subscription
#        exclude = ('tags',)


class ContactSubscriptionView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        return render_to_response(get_skin_relative_path('views/contact/subscriptions.html'),
            RequestContext(request, { 'association': a,
                                      'contact': c }))


class ContactSubscriptionAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactSubscriptionAddView, self).__init__()
        self.cls = Subscription
        self.form = SubscriptionForm
        #self.custom_form = SubscriptionCustomFieldsForm
        self.title = _('Adding new subscription for ')
        self.section_title = _('Subscription data')
        self.section_icon = 'fa-book'
        self.submit_text = _('Create new subscription')
        self.success_text = _('Subscription created successfully.')
        self.error_text = _('Cannot save the subscription.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_subscriptions', args=args)


class ContactSubscriptionEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactSubscriptionEditView, self).__init__()
        self.cls = Subscription
        self.form = SubscriptionForm
        #self.custom_form = SubscriptionCustomFieldsForm
        self.title = _('Editing subscription for ')
        self.section_title = _('Subscription data')
        self.section_icon = 'fa-book'
        self.submit_text = _('Save subscription')
        self.success_text = _('Subscription modified successfully.')
        self.error_text = _('Cannot save the subscription.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_subscriptions', args=args)


class ContactSubscriptionDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactSubscriptionDeleteView, self).__init__()
        self.cls = Subscription
        self.success_text = _('Subscription deleted successfully.')
        self.error_text = _('Cannot delete the subscription.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_subscriptions', args=args)


#==============================================================================
class ContactPartecipationView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        return render_to_response(get_skin_relative_path('views/contact/partecipations.html'),
            RequestContext(request, { 'association': a,
                                      'contact': c }))


#==============================================================================
class RelationshipForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        a = kwargs.pop('association')
        c = kwargs.pop('contact')
        super(RelationshipForm, self).__init__(*args, **kwargs)
        if a:
            self.fields['type'].queryset = RelationshipType.objects.filter(association=a)
            self.fields['to_contact'].queryset = Contact.objects.filter(association=a)
            if c:
                self.fields['to_contact'].queryset = self.fields['to_contact'].queryset.exclude(pk=c.pk)

    class Meta:
        model = Relationship
        exclude = ('from_contact',
                   'tags',)


class ContactRelationshipView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        contact = kwargs.get('contact')

        c = get_object_or_404(Contact, _uuid=contact)
        # TODO - check security
        a = c.association

        return render_to_response(get_skin_relative_path('views/contact/relationships.html'),
            RequestContext(request, { 'association': a,
                                      'contact': c }))


class ContactRelationshipAddView(GenericContactInlineAddView):
    def __init__(self):
        super(ContactRelationshipAddView, self).__init__()
        self.cls = Relationship
        self.form = RelationshipForm
        self.contact_fieldname = 'from_contact'
        self.title = _('Adding new relationship for ')
        self.section_title = _('Relationship data')
        self.section_icon = 'fa-child'
        self.submit_text = _('Create new relationship')
        self.success_text = _('Relationship created successfully.')
        self.error_text = _('Cannot save the relationship.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_relationships', args=args)


class ContactRelationshipEditView(GenericContactInlineEditView):
    def __init__(self):
        super(ContactRelationshipEditView, self).__init__()
        self.cls = Relationship
        self.form = RelationshipForm
        self.contact_fieldname = 'from_contact'
        self.title = _('Editing relationship for ')
        self.section_title = _('Relationship data')
        self.section_icon = 'fa-child'
        self.submit_text = _('Save relationship')
        self.success_text = _('Relationship modified successfully.')
        self.error_text = _('Cannot save the relationship.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_relationships', args=args)


class ContactRelationshipDeleteView(GenericContactInlineDeleteView):
    def __init__(self):
        super(ContactRelationshipDeleteView, self).__init__()
        self.cls = Relationship
        self.contact_fieldname = 'from_contact'
        self.success_text = _('Relationship deleted successfully.')
        self.error_text = _('Cannot delete the relationship.')

    def redirect_url(self, *args):
        return reverse('nublas:contact_relationships', args=args)


#==============================================================================
class ContactAutoCompleteView(View):
    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        association = kwargs.get('association')

        result = []
        searchtext = request.GET['q']
        if len(searchtext) >= 2:
            query = Q(first_name__icontains=searchtext) | \
                    Q(middle_name__icontains=searchtext) | \
                    Q(last_name__icontains=searchtext)
            items = Contact.objects.filter(Q(association___uuid=association) & query).order_by('last_name')[:10]
            for item in items:
                result.append((item.pk, str(item))) # TODO - handle uuid ?

        return HttpResponse(json.dumps(result))
