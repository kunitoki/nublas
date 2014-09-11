from .conf import settings

if settings.ENABLE_MULTILANGUAGE and 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.translator import translator, TranslationOptions

    from .models import Association

    class AssociationTranslationOptions(TranslationOptions):
        fields = ('name', 'description',)
    translator.register(Association, AssociationTranslationOptions)
