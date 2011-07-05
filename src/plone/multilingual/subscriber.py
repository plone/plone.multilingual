from zope import component
from plone.multilingual.interfaces import ILanguage, ITranslationManager
from zope.intid.interfaces import IIntIds


# unregister the translation before the object will be removed
def remove_translation_on_delete(obj, event):
    # deleting a complete plone-portal throws error, because IIntId
    # is not found anymore
    if component.queryUtility(IIntIds, None) is not None:
        language = ILanguage(obj).get_language()
        ITranslationManager(obj).remove_translation(language)


# update the translation on Modified (because the language could be modified)
def update_on_modify(obj, event):
    if component.queryUtility(IIntIds, None) is not None:
        ITranslationManager(obj).update()
