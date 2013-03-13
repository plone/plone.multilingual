from plone.app.content.interfaces import INameFromTitle
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.multilingual.interfaces import ITranslationManager

from zope.component import adapter
from zope.component import queryUtility, getUtility
from zope.container.interfaces import INameChooser

from zope.event import notify
from zope.lifecycleevent import ObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from plone.uuid.interfaces import IUUIDGenerator

from plone.multilingual.interfaces import ATTRIBUTE_NAME, NEW_TRANSLATION, \
    ITranslatable

try:
    from Acquisition import aq_base, aq_parent
except ImportError:
    aq_base = lambda v: v  # soft-dependency on Zope2, fallback


@adapter(ITranslatable, IObjectCreatedEvent)
def addAttributeTG(obj, event):

    if not IObjectCopiedEvent.providedBy(event):
        if getattr(aq_base(obj), ATTRIBUTE_NAME, None):
            return  # defensive: keep existing TG on non-copy create

    generator = queryUtility(IUUIDGenerator)
    if generator is None:
        return

    tg = generator()
    if not tg:
        return

    setattr(obj, ATTRIBUTE_NAME, tg)

    # also mark the item as new translation
    setattr(obj, NEW_TRANSLATION, True)


@adapter(ITranslatable, IObjectModifiedEvent)
def renameOnEdit(obj, event):

    # skip if the title is empty, obj has just been created
    if obj.Title() == '':
        return
    if getattr(obj, NEW_TRANSLATION, None):
        setattr(obj, NEW_TRANSLATION, False)
        manager = ITranslationManager(obj)
        # don't do anything if there are no translations - renaming will be
        # handled by Plone
        if len(manager.get_translated_languages()) > 1:
            old_id = obj.id
            # If the obj does not provide INameFromTitle, use the ID normalizer
            # to create an id
            if not INameFromTitle(obj, None):
                normalizer = getUtility(IIDNormalizer)
                name = normalizer.normalize(obj.Title())
            else:
                name = None
            parent = aq_parent(obj)
            chooser = INameChooser(parent)
            new_id = chooser.chooseName(name, obj)

            if new_id != old_id:
                if getattr(aq_base(obj), 'setId', None):
                    obj.setId(new_id)
                    notify(ObjectMovedEvent(
                        obj, parent, old_id, parent, new_id))
                else:
                    parent.manage_renameObject(old_id, new_id)
