from plone.multilingual.interfaces import (
    ITranslationLocator,
    ILanguage)
from Acquisition import aq_parent
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from Products.CMFCore.interfaces._content import IFolderish
from plone.app.folder.utils import findObjects


def multilingualMoveObject(content, language):
    """ 
    Move content object and its contained objects to a new language folder
    Also set the language on all the content moved
    """
    target_folder = ITranslationLocator(content)(language)
    ILanguage(content).set_language(language)
    # We need to check if it's IFolderish to change languages recursive
    if IFolderish.providedBy(content):
        for path, obj in findObjects(content):
            ILanguage(obj).set_language(language)
    parent = aq_parent(content)
    cb_copy_data = parent.manage_cutObjects(content.getId())
    list_ids = target_folder.manage_pasteObjects(cb_copy_data)
    new_id = list_ids[0]['new_id']
    new_object = target_folder[new_id]
    # Throw ObjectModified Event
    new_object.reindexObject()
    # This will reallocate the TranslationManager
    notify(ObjectModifiedEvent(new_object))
    return new_object
