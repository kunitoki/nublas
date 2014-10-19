from __future__ import unicode_literals
import re
import itertools
from django import forms
from django.forms.models import ModelFormOptions
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from ..conf import settings


#==============================================================================
# Inspiration: http://schinckel.net/2013/06/14/django-fieldsets/

_old_init = ModelFormOptions.__init__

def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, 'fieldsets', None)

ModelFormOptions.__init__ = _new_init


#==============================================================================
class Fieldline(object):
    def __init__(self, form, fieldline, layoutline):
        self.form = form  # A django.forms.Form instance
        if not hasattr(fieldline, "__iter__") or isinstance(fieldline, six.text_type):
            self.fields = [fieldline]
        else:
            self.fields = fieldline
        if not hasattr(layoutline, "__iter__") or isinstance(fieldline, six.integer_types):
            self.layout = [layoutline]
        else:
            self.layout = layoutline

    def __iter__(self):
        total_cols = 12
        first_label_cols = 2
        layout_cols = total_cols - first_label_cols
        if len(self.fields) > 1:
            layout_cols = int(layout_cols / len(self.fields) - 1)

        for field, layout in itertools.izip_longest(self.fields, self.layout):
            yield self.form[field], layout if layout else layout_cols


class Fieldset(object):
    def __init__(self, form, legend, fields, layout, classes):
        self.form = form
        self.legend = legend
        self.fields = fields
        self.layout = layout
        self.classes = classes

    def __iter__(self):
        # Similar to how a form can iterate through it's fields...
        for fieldline, layoutline in itertools.izip_longest(self.fields, self.layout):
            yield Fieldline(
                form=self.form,
                fieldline=fieldline,
                layoutline=layoutline
            )


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
                layout=data.get('layout', tuple()),
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
                    if isinstance(v, six.text_type):
                        v = v.strip()
                    new_vs.append(v)
                data.setlist(k, new_vs)
            self.data = data


#==============================================================================
class ReadonlyForm(object):
    def set_readonly(self, is_readonly=True):
        for field in self.fields:
            self.fields[field].is_readonly = is_readonly


#==============================================================================
class TagsForm(object):
    def has_tags(self):
        for field in self:
            if field.name == 'tags' and field.value() is not None:
                return True if len(field.value()) > 0 else False
        return False


#==============================================================================
class DefaultWidgetsForm(object):
    def _update_default_widgets(self):
        """
        Returns custom widgets for each field type
        """
        # TODO - implement this for all the fields we need !
        # TODO - must check this for default values
        # TODO - must updates original widget attributes
        for field in self.fields:
            f = self.fields[field]
            #if isinstance(f, forms.FloatField):
            #    f.widget = spinner.SpinnerWidget(attrs={ 'max_value': f.max_value, 'min_value': f.min_value })
            #elif isinstance(f, forms.IntegerField):
            #    f.widget = spinner.IntegerSpinnerWidget(attrs={ 'max_value': f.max_value, 'min_value': f.min_value })
            #elif isinstance(f, forms.DateField):
            #    f.widget = date.DatePickerWidget()
            #elif isinstance(f, forms.DateTimeField):
            #    f.widget = date.DateTimePickerWidget() # TODO - testing
            #elif isinstance(f, forms.TimeField):
            #    f.widget = date.TimePickerWidget()
            # TODO - think a way to reuse this in different apps
            #elif isinstance(f, forms.ChoiceField):
            #    placeholder = f.empty_value if hasattr(f, 'empty_value') else None
            #    f.widget = select.SelectReplacementWidget(choices=f.choices, placeholder=placeholder)
            #elif isinstance(f, forms.TypedChoiceField):
            #    placeholder = f.empty_value if hasattr(f, 'empty_value') else None
            #    f.widget = select.SelectReplacementWidget(choices=f.choices, placeholder=placeholder)


#==============================================================================
class WidgetErrorStateForm(object):
    def _update_widgets_error_state(self):
        if self.errors:
            for name in self.errors:
                if name in self.fields:
                    classes = self.fields[name].widget.attrs.get('class', '')
                    classes += ' has-error' if len(classes) > 0 else 'has-error'
                    self.fields[name].widget.attrs['class'] = classes


#==============================================================================
class BaseForm(ValidatingForm, FieldsetForm, ReadonlyForm, TagsForm, WidgetErrorStateForm, DefaultWidgetsForm, forms.Form):
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
        # Update default widgets
        self._update_default_widgets()
        # Notify about errors all widgets
        self._update_widgets_error_state()
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
class BaseModelForm(ValidatingForm, FieldsetForm, ReadonlyForm, TagsForm, WidgetErrorStateForm, DefaultWidgetsForm, forms.ModelForm):
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
        # Update default widgets
        self._update_default_widgets()
        # Notify about errors all widgets
        self._update_widgets_error_state()
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
