import re
from django import forms
from django.forms.models import ModelFormOptions
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from ..conf import settings

from taggit.forms import TagField


#==============================================================================
# Inspiration: http://schinckel.net/2013/06/14/django-fieldsets/

_old_init = ModelFormOptions.__init__

def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, 'fieldsets', None)

ModelFormOptions.__init__ = _new_init


#==============================================================================
class Fieldline(object):
    def __init__(self, form, field_or_fields):
        self.form = form  # A django.forms.Form instance
        if not hasattr(field_or_fields, "__iter__") or isinstance(field_or_fields, six.text_type):
            self.fields = [field_or_fields]
        else:
            self.fields = field_or_fields

    def __iter__(self):
        total_size = 12
        first_label = 2
        remaining_size = total_size - first_label
        if len(self.fields) > 1:
            remaining_size = remaining_size / len(self.fields) - 1
        for index, field in enumerate(self.fields):
            yield self.form[field], remaining_size


class Fieldset(object):
    def __init__(self, form, legend, fields, classes):
        self.form = form
        self.legend = legend
        self.fields = fields
        self.classes = classes

    def __iter__(self):
        # Similar to how a form can iterate through it's fields...
        for field_or_fields in self.fields:
            yield Fieldline(
                form=self.form,
                field_or_fields=field_or_fields
            )


#==============================================================================
class FieldsetForm(object):
    def _build_fieldsets(self):
        meta = getattr(self, '_meta', None)
        if not meta:
            meta = getattr(self, 'Meta', None)
        if not meta or not meta.fieldsets:
            return

        self._fieldsets_meta = meta.fieldsets
        self.fieldsets = self._fieldsets

    def _fieldsets(self):
        if not self._fieldsets_meta:
            return

        for legend, data in self._fieldsets_meta:
            yield Fieldset(
                form=self,
                legend=legend,
                fields=data.get('fields', tuple()),
                classes=data.get('classes', '')
            )


#==============================================================================
class ValidatingForm(object):
    def _full_clean(self):
        """
        Strip whitespace automatically in all form fields
        """
        if hasattr(self, 'data') and self.data \
               and hasattr(self.data, 'lists') and self.data.lists:
            data = self.data.copy()
            for k, vs in self.data.lists():
                new_vs = []
                for v in vs:
                    if isinstance(v, basestring):
                        v = v.strip()
                    new_vs.append(v)
                data.setlist(k, new_vs)
            self.data = data


#==============================================================================
class ReadonlyForm(object):
    def set_readonly(self, is_readonly=True):
        for f in self.fields:
            self.fields[f].is_readonly = is_readonly


#==============================================================================
class BaseForm(ValidatingForm, FieldsetForm, ReadonlyForm, forms.Form):
    """
    Base forms for all unbounded forms in our pages.
    It provides a custom way to initialize widgets from a set of parameters
    """
    def __init__(self, *args, **kwargs):
        # Search for initial values
        initial = None
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
        # Construct form
        super(BaseForm, self).__init__(*args, **kwargs)
        # Update fieldsets
        self._build_fieldsets()
        # Initialize values from initial parameters
        if initial:
            for key, value in initial.items():
                try:
                    self.fields[key].initial = value
                except KeyError: # Ignore unexpected parameters
                    pass

    def full_clean(self):
        self._full_clean()
        super(BaseForm, self).full_clean()


#==============================================================================
class BaseModelForm(ValidatingForm, FieldsetForm, ReadonlyForm, forms.ModelForm):
    """
    Base forms for all bounded forms to models.
    It provides a custom way to initialize widgets from a set of parameters
    """
    def __init__(self, *args, **kwargs):
        # Search for initial values
        initial = None
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
        # Construct form
        super(BaseModelForm, self).__init__(*args, **kwargs)
        # Update fieldsets
        self._build_fieldsets()
        # Initialize values from initial parameters
        if initial:
            for key, value in initial.items():
                try:
                    self.fields[key].initial = value
                except KeyError: # Ignore unexpected parameters
                    pass

    def full_clean(self):
        self._full_clean()
        super(BaseModelForm, self).full_clean()


#==============================================================================
class BaseModelTagsForm(BaseModelForm):
    """
    Base form for adding tags to our models
    """
    tags = TagField(required=False)

    def has_tags(self):
        t = []
        for field in self:
            if field.name == 'tags' and field.value() is not None:
                t = field.value()
                break
        return True if len(t) > 0 else False


#==============================================================================
class BaseAuthValidatingForm(BaseForm):
    """
    Validating usernames and password form
    """
    def validate_new_username(self, username, and_query=None):
        if re.search('\s+', username):
            raise forms.ValidationError(_('The username cannot contain spaces.'))
        # TODO - check for username minimum length
        UserModel = get_user_model()
        try:
            query = Q(username=username)
            if and_query: query &= and_query
            UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(_('The username "%s" is already taken.') % username)

    def validate_existing_username(self, username, and_query=None):
        if re.search('\s+', username):
            raise forms.ValidationError(_('The username cannot contain spaces.'))
        # TODO - check for username minimum length
        UserModel = get_user_model()
        try:
            query = Q(username=username)
            if and_query: query &= and_query
            UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            raise forms.ValidationError(_('The username "%s" does not exists.') % username)
        return username

    def validate_new_email(self, email, and_query=None):
        UserModel = get_user_model()
        try:
            query = Q(email=email)
            if and_query: query &= and_query
            UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            return email
        raise forms.ValidationError(_('The email "%s" is already taken.') % email)

    def validate_existing_email(self, email, and_query=None):
        UserModel = get_user_model()
        try:
            query = Q(email=email)
            if and_query: query &= and_query
            UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            raise forms.ValidationError(_('The email "%s" does not exists.') % email)
        return email

    def validate_password(self, pwd, strict=True):
        if strict or len(pwd) > 0:
            if re.search('\s+', pwd):
                raise forms.ValidationError(_('The password cannot contain spaces.'))
            if len(pwd) < settings.AUTH_PASSWORD_MIN_LENGTH:
                raise forms.ValidationError(_('The password must be at least %d characters.' % settings.AUTH_PASSWORD_MIN_LENGTH))
        return pwd

    def validate_passwords(self, pwd1, pwd2):
        if pwd1 == pwd2:
            return True
        return False
