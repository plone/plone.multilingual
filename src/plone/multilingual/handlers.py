from zope.component import adapter
from zope.component import queryUtility

from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent

from plone.uuid.interfaces import IUUIDGenerator

from plone.multilingual.interfaces import ATTRIBUTE_NAME, ITranslatable

try:
    from Acquisition import aq_base
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
