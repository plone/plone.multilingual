from Acquisition import aq_parent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.multilingual.interfaces import (
    LANGUAGE_INDEPENDENT,
    ITranslationManager,
    ILanguage)

# unregister the translation before the object will be removed
def remove_translation_on_delete(obj, event):
    language = ILanguage(obj).get_language()
    ITranslationManager(obj).remove_translation(language)


# check if the parent folder is neutral and assigns neutral language to the content object
# In case is a normal content update translation manager with the new language
def update_on_modify(obj, event):
    parent = aq_parent(obj)
    if (not IPloneSiteRoot.providedBy(parent)) and ILanguage(parent).get_language() == LANGUAGE_INDEPENDENT:
        ILanguage(obj).set_language(LANGUAGE_INDEPENDENT)
    obj.reindexObject()
    ITranslationManager(obj).update()
