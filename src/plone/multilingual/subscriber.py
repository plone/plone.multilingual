from plone.multilingual.interfaces import ILanguage, ITranslationManager


# unregister the translation before the object will be removed
def remove_translation_on_delete(obj, event):
    language = ILanguage(obj).get_language()
    ITranslationManager(obj).remove_translation(language)


# update the translation on Modified (because the language could be modified)
def update_on_modify(obj, event):
    ITranslationManager(obj).update()
