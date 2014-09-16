from django import forms
from django.db import models

from taggit.forms import TagField


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
class CustomWidgetsForm(object):
    def _update_fields_widget(self):
        """
        Returns custom widgets for each field type
        """
        # TODO - implement this for all the fields we need !
        # TODO - must check this for default values
        # TODO - must updates original widget attributes
        for field in self.fields:
            f = self.fields[field]
            #if isinstance(f, forms.FloatField):
            #    #f.widget = spinner.SpinnerWidget(attrs={ 'max_value': f.max_value, 'min_value': f.min_value })


#==============================================================================
class BaseForm(ValidatingForm, CustomWidgetsForm, forms.Form):
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
        # Update widgets type
        self._update_fields_widget()
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
class BaseModelForm(ValidatingForm, CustomWidgetsForm, forms.ModelForm):
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
        # Update widgets type
        self._update_fields_widget()
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
