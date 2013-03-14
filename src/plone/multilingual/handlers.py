from plone.app.content.interfaces import INameFromTitle
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.locking.interfaces import ILockable
from plone.multilingual.interfaces import ITranslationManager, ILanguage

from zope.component import adapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser

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

    # also mark the item as new translation, unless it is language-neutral
    if ILanguage(obj).get_language() != '':
        setattr(obj, NEW_TRANSLATION, True)


@adapter(ITranslatable, IObjectModifiedEvent)
def renameOnEdit(obj, event):
    # Don't rename navigation roots
    if INavigationRoot.providedBy(obj):
        return
    # skip if the title is empty, obj has just been created
    if obj.Title() == '':
        return
    if getattr(obj, NEW_TRANSLATION, None):
        setattr(obj, NEW_TRANSLATION, False)
        manager = ITranslationManager(obj, None)
        # don't do anything if there are no translations yet - renaming
        # will be handled by Plone
        if manager and len(manager.get_translated_languages()) > 1:
            old_id = obj.id
            # If the obj does not provide INameFromTitle, use the ID normalizer
            # to create an id
            if not INameFromTitle(obj, None):
                normalizer = IUserPreferredURLNormalizer(obj.REQUEST)
                title = obj.Title()
                if not isinstance(title, unicode):
                    title = title.decode('utf-8')
                name = normalizer.normalize(title)
            else:
                name = None
            parent = aq_parent(obj)
            chooser = INameChooser(parent)
            new_id = chooser.chooseName(name, obj)

            if new_id != old_id:
                lockable = ILockable(obj)
                if lockable.locked():
                    if lockable.can_safely_unlock():
                        lockable.unlock()
                    else:
                        # cant' do anything
                        return
                parent.manage_renameObject(old_id, new_id)
