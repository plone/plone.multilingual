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


def remove_translation_on_delete(obj, event):
    pass


# In case is a normal content update translation manager with the new language
def update_on_modify(obj, event):
    ITranslationManager(obj).update()


def set_recursive_language(obj, language):
    """ Set the language at this object and recursive
    """
    ILanguage(obj).set_language(language)
    modified(obj)  # XXX: this will create recursion, disabled
    if IFolderish.providedBy(obj):
        for item in obj.items():
            if ITranslatable.providedBy(item):
                set_recursive_language(item, language)


# Subscriber to set language on the child folder
def createdEvent(obj, event):

    # On ObjectCopiedEvent and ObjectMovedEvent aq_parent(event.object) is
    # always equal to event.newParent.
    parent = aq_parent(event.object)

    if ITranslatable.providedBy(parent):
        # Normal use case
        # We set the tg, linking
        language = ILanguage(parent).get_language()
        set_recursive_language(obj, language)
        sdm = obj.session_data_manager
        session = sdm.getSessionData()
        portal = getSite()

        if 'tg' in session.keys() and \
           not portal.portal_factory.isTemporary(obj):
            IMutableTG(obj).set(session['tg'])
            modified(obj)
            del session['tg']
    else:
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)
