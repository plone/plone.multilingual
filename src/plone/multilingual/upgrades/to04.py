from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ITranslationLocator
from plone.multilingual.interfaces import ITranslationIdChooser
from plone.multilingual.interfaces import ITranslationCloner
from plone.multilingual.interfaces import ITranslationFactory
from plone.multilingual.factory import DefaultTranslationFactory
from plone.multilingual.factory import DefaultTranslationIdChooser
from plone.multilingual.factory import DefaultTranslationLocator
from plone.multilingual.manager import TranslationManager
from plone.multilingual.factory import DefaultTranslationCloner
from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ILanguageIndependentFieldsManager
from archetypes.multilingual.interfaces import IArchetypesTranslatable
from archetypes.multilingual.utils import LanguageIndependentFieldsManager
from archetypes.multilingual.cloner import Cloner
from plone.multilingualbehavior.interfaces import IDexterityTranslatable
from plone.dexterity.interfaces import IEditFinishedEvent
from plone.multilingualbehavior.cloner import Cloner as Cloner_bh
from plone.multilingualbehavior.utils import LanguageIndependentFieldsManager as LanguageIndependentFieldsManager_bh
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent

from zope.component.hooks import getSite
import transaction


def upgrade(context):
    # Unregister remaining adapter registration
    sm = getSite().getSiteManager()
    sm.unregisterAdapter(factory=DefaultTranslationFactory, required=(ITranslatable, ), provided=ITranslationFactory)
    sm.unregisterAdapter(factory=DefaultTranslationIdChooser, required=(ITranslatable, ), provided=ITranslationIdChooser)
    sm.unregisterAdapter(factory=DefaultTranslationLocator, required=(ITranslatable, ), provided=ITranslationLocator)
    sm.unregisterAdapter(factory=TranslationManager, required=(ITranslatable, ), provided=ITranslationManager)
    sm.unregisterAdapter(factory=DefaultTranslationCloner, required=(ITranslatable, ), provided=ITranslationCloner)
    sm.unregisterAdapter(factory=Cloner, required=(IArchetypesTranslatable, ), provided=ITranslationCloner)
    sm.unregisterAdapter(factory=LanguageIndependentFieldsManager, required=(IArchetypesTranslatable, ), provided=ILanguageIndependentFieldsManager)
    sm.unregisterHandler(required=(IDexterityTranslatable, IEditFinishedEvent))
    sm.unregisterAdapter(factory=Cloner_bh, required=(IDexterityTranslatable, ), provided=ITranslationCloner)
    sm.unregisterAdapter(factory=LanguageIndependentFieldsManager_bh, required=(IDexterityTranslatable, ), provided=ILanguageIndependentFieldsManager)
    sm.unregisterHandler(required=(ITranslatable, IObjectModifiedEvent))
    sm.unregisterHandler(required=(ITranslatable, IObjectAddedEvent))
    sm.unregisterHandler(required=(ITranslatable, IObjectCopiedEvent))
    sm.unregisterHandler(required=(ITranslatable, IObjectMovedEvent))

    transaction.commit()
    app = getSite().restrictedTraverse('/')
    app._p_jar.sync()
