from plone.multilingual.interfaces import (
    ITranslationLocator,
    ILanguage)
from Acquisition import aq_parent
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


def multilingualMoveObject(content, language):
    """ Move content object to it's folder
    """
    target_folder = ITranslationLocator(content)(language)
    ILanguage(content).set_language(language)
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
