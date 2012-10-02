from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.multilingual.interfaces import (
    LANGUAGE_INDEPENDENT,
    ITranslationManager,
    ITranslatable,
    ILanguage)
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.lifecycleevent import modified
from Products.CMFCore.interfaces import IFolderish


# unregister the translation before the object will be removed
def remove_translation_on_delete(obj, event):
    language = ILanguage(obj).get_language()
    ITranslationManager(obj).remove_translation(language)


# In case is a normal content update translation manager with the new language
def update_on_modify(obj, event):
    ITranslationManager(obj).update()


def set_recursive_language(obj, language):
    """ Set the language at this object and recursive
    """
    ILanguage(obj).set_language(language)
    modified(obj)
    if IFolderish.providedBy(obj):
        for item in obj.items():
            if ITranslatable.providedBy(item):
                set_recursive_language(item, language)


# Subscriber to set language on the child folder
def createdEvent(obj, event):
    portal = getSite()
    parent = event.newParent
    language_tool = getToolByName(portal, 'portal_languages')
    if (language_tool.startNeutral() and
        ITranslatable.providedBy(obj)):
        # We leave this untouched by now.
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)
    elif (IPloneSiteRoot.providedBy(parent) and
          ITranslatable.providedBy(obj) and
          ILanguage(obj).get_language() == LANGUAGE_INDEPENDENT):
        pl = getToolByName(portal, "portal_languages")
        language = pl.getPreferredLanguage()
        set_recursive_language(obj, language)
    elif ITranslatable.providedBy(parent):
        language = ILanguage(parent).get_language()
        set_recursive_language(obj, language)
