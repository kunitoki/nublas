from .conf import settings

if settings.ENABLE_MULTILANGUAGE and 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.translator import translator, TranslationOptions

    from .models import (Country)

    class CountryTranslationOptions(TranslationOptions):
        fields = ('name',)
    translator.register(Country, CountryTranslationOptions)
