# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import IMutableTG
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ITranslatable
from zope.component.hooks import getSite
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


def remove_translation_on_delete(obj, event):
    pass


# In case is a normal content update translation manager with the new language
def update_on_modify(obj, event):
    ITranslationManager(obj).update()


def set_recursive_language(obj, language):
    """ Set the language at this object and recursive
    """
    ILanguage(obj).set_language(language)
    # XXX: this will create recursion, disabled
    # modified(obj)

    # update translations for each object
    update_on_modify(obj, None)
    if IFolderish.providedBy(obj):
        for item in obj.items():
            if ITranslatable.providedBy(item):
                set_recursive_language(item, language)


# Subscriber to set language on the child folder
def createdEvent(obj, event):
    """ It can be a 
        IObjectRemovedEvent - don't do anything
        IObjectMovedEvent
        IObjectAddedEvent
        IObjectCopiedEvent
    """
    if IObjectRemovedEvent.providedBy(event):
        return

    portal = getSite()
    language_tool = getToolByName(portal, 'portal_languages')

    # On ObjectCopiedEvent and ObjectMovedEvent aq_parent(event.object) is
    # always equal to event.newParent.
    parent = aq_parent(event.object)

    if (language_tool.startNeutral() and ITranslatable.providedBy(obj)):

        # We leave this untouched by now.
        # We don't set languages
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)

    elif (IPloneSiteRoot.providedBy(parent) and
          ITranslatable.providedBy(obj) and
          ILanguage(obj).get_language() == LANGUAGE_INDEPENDENT):

        # It's a root folder and we set the default language
        # ( not independent allowed )
        language = language_tool.getPreferredLanguage()
        set_recursive_language(obj, language)

    elif ITranslatable.providedBy(parent):
        # Normal use case
        # We set the tg, linking
        language = ILanguage(parent).get_language()
        set_recursive_language(obj, language)
        sdm = obj.session_data_manager
        session = sdm.getSessionData()

        if 'tg' in session.keys() and \
           not portal.portal_factory.isTemporary(obj):
            IMutableTG(obj).set(session['tg'])
            modified(obj)
            del session['tg']
