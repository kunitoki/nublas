from django.forms.models import model_to_dict


#==============================================================================
class UniqueBooleanModelMixin(object):
    """
    A model mixin that implements unique booleans
    """

    def _unique_boolean_pre_save(self):
        unique_boolean = getattr(self, 'UNIQUE_BOOLEAN', [])
        for field in unique_boolean:
            # build filter
            filter_kwargs = { field[0]: True }
            for arg in field[1]:
                if getattr(self, arg):
                    filter_kwargs[arg] = getattr(self, arg)
            print(filter_kwargs)
            # main logic
            if getattr(self, field[0]):
                tmp = self.__class__.objects.filter(**filter_kwargs).exclude(pk=self.pk)
                for t in tmp:
                    setattr(t, field[0], False)
                    t.save()
            else:
                if self.__class__.objects.filter(**filter_kwargs).count() == 0:
                    setattr(self, field[0], True)

    def _unique_boolean_pre_delete(self):
        unique_boolean = getattr(self, 'UNIQUE_BOOLEAN', [])
        for field in unique_boolean:
            # build filter
            filter_kwargs = { field[0]: True }
            for arg in field[1]:
                if getattr(self, arg):
                    filter_kwargs[arg] = getattr(self, arg)
            # main logic
            tmp = self.__class__.objects.filter(**filter_kwargs)
            if len(tmp) > 0:
                setattr(tmp[0], field[0], True)
                tmp[0].save()


#==============================================================================
class UtilityModelMixin(object):
    """
    Options utility for model instances to return private api in a conveniente
    and wrappable interface.
    """

    def get_model(self):
        """ Returns the model meta """
        return self._meta

    def get_name(self):
        """ Returns the singular name of the model """
        return "%s" % self._meta.name

    def get_verbose_name(self):
        """ Returns the singular verbose name of the model """
        return "%s" % self._meta.verbose_name

    def get_fields(self):
        """ Get all fields and their display strings """
        return [(f, self.get_field_display(f)) for f in self._meta.fields]

    def get_field_display(self, field):
        """
        Override function to obtain field values to be used in display lists

        :param field: field instance to display
        :return: string display of field
        """
        return field.value_to_string(self)

    def get_field_by_name(self, field_name):
        """
        Return a field object by name

        :param field_name: field name
        :return: field instance
        """
        return self._meta.get_field_by_name(field_name)

    def to_dict(self, fields=None, exclude=None):
        """
        Return the model instance as a dictionary

        :param fields: which fields to use
        :param exclude: which fields to exclude
        :return: dict()
        """
        return model_to_dict(self, fields=fields, exclude=exclude)
