from zope import interface
from zope.event import notify
from plone.uuid.interfaces import IUUID
from plone.multilingual.interfaces import (
    ILanguage,
    ITranslationManager,
    ITranslationFactory,
    ITG,
    IMutableTG,
    NOTG
)
from plone.multilingual.handlers import addAttributeTG
from plone.multilingual.events import (
    ObjectWillBeTranslatedEvent,
    ObjectTranslatedEvent,
)
from plone.uuid.handlers import addAttributeUUID
from plone.app.uuid.utils import uuidToObject
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName


class TranslationManager(object):

    interface.implements(ITranslationManager)

    def __init__(self, context):
        self.context = context
        if isinstance(context, str):
            self.tg = context
        else:
            self.tg = self.get_tg(context)
        self._canonical = None
        site = getSite()
        self.pcatalog = getToolByName(site, 'portal_catalog', None)

    def get_id(self, context):
        """If an object is created via portal factory we don't get a id, we
           have to wait till the object is really created.
           TODO: a better check if we are in the portal factory!
        """
        try:
            context_id = IUUID(context)
        # We must ensure that this case can't happen, any object translatable
        # will have an UUID (in any case we can be at the portal factory!)
        except KeyError:
            addAttributeUUID(context, None)
            context.reindexObject(idxs=['UID'])
            context_id = IUUID(context)
        return context_id

    def get_tg(self, context):
        """If an object is created via portal factory we don't get a id, we
           have to wait till the object is really created.
           TODO: a better check if we are in the portal factory!
        """
        try:
            context_id = ITG(context)
        # We must ensure that this case can't happen, any object translatable
        # will have an UUID (in any case we can be at the portal factory!)
        except TypeError:
            addAttributeTG(context, None)
            context.reindexObject(idxs=['TranslationGroup'])
            context_id = ITG(context)
        return context_id

    def query_canonical(self):
        return self.tg

    def register_translation(self, language, content):
        """ register a translation for an existing content """
        if not language and language != '':
            raise KeyError('There is no target language')

        if type(content) == str:
            content_obj = uuidToObject(content)
        else:
            content_obj = content

        # Check if exists and is not myself
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg, Language=language)
        if len(brains) > 0 and brains[0].UID != self.get_id(content_obj):
            raise KeyError("Translation already exists")

        # register the new translation in the canonical
        IMutableTG(content_obj).set(self.tg)
        content_obj.reindexObject()

        return

    def update(self):
        """ see interfaces"""
        language = ILanguage(self.context).get_language()
        self.context.reindexObject()
        # In case language is already on the translated languages we are going to orphan the old translation
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg, Language=language)
        if len(brains) == 0:
            # There is not a translation with this tg on this language
            self.register_translation(language, self.context)
        else:
            # We need to check if the language has changed
            brain = brains[0]
            content_id = self.get_id(self.context)
            if brain.UID != content_id:
                # Is a different object -> remove the old one
                # We get the old uuid
                old_object = brain.getObject()
                IMutableTG(old_object).set(NOTG)
                old_object.reindexObject()

    def add_translation(self, language):
        """ see interfaces """
        if not language and language != '':
            raise KeyError('There is no target language')
        # event
        notify(ObjectWillBeTranslatedEvent(self.context, language))
        # create the translated object
        translation_factory = ITranslationFactory(self.context)
        translated_object = translation_factory(language)
        ILanguage(translated_object).set_language(language)
        # reindex the translated object
        translated_object.reindexObject()
        # register the new translation
        self.register_translation(language, translated_object)
        # event
        notify(ObjectTranslatedEvent(self.context, \
            translated_object, language))
        return

    def remove_translation(self, language):
        """ see interfaces """
        translation = self.get_translation(language)
        IMutableTG(translation).set(NOTG)
        translation.reindexObject()

    def get_translation(self, language):
        """ see interfaces """
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg, Language=language)
        if len(brains) != 1:
            return None
        return brains[0].getObject()

    def get_translations(self):
        """ see interfaces """
        translations = {}
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg)
        for brain in brains:
            translations[brain.Language] = brain.getObject()
        return translations

    def get_restricted_translations(self):
        """ see interfaces """
        translations = {}
        brains = self.pcatalog.searchResults(TranslationGroup=self.tg,
            Language='all')
        for brain in brains:
            translations[brain.Language] = brain.getObject()
        return translations

    def get_translated_languages(self):
        """ see interfaces """
        languages = []
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg)
        for brain in brains:
            languages.append(brain.Language)
        return languages

    def has_translation(self, language):
        """ see interfaces """
        return language in self.get_translated_languages()
