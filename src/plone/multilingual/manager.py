from zope import interface
from zope.event import notify
from zope.component import getUtility
from plone.uuid.interfaces import IUUID
from plone.multilingual.interfaces import (
    ILanguage,
    ITranslationManager,
    ITranslationFactory,
    IMultilingualStorage,
)
from plone.multilingual.canonical import Canonical
from plone.multilingual.events import (
    ObjectWillBeTranslatedEvent,
    ObjectTranslatedEvent,
)
from plone.uuid.handlers import addAttributeUUID
from plone.app.uuid.utils import uuidToObject


class TranslationManager(object):

    interface.implements(ITranslationManager)

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

    def __init__(self, context):
        self.context = context

    def _get_or_create(self):
        """ get the canonical for context
            (create it, if it's not existing)
        """
        canonical = self._get_canonical()
        if canonical is None:
            canonical = self._add_canonical()
        return canonical

    def _get_canonical(self):
        """ get the canonical for context """
        storage = getUtility(IMultilingualStorage)
        context_id = self.get_id(self.context)
        canonical = storage.get_canonical(context_id)
        return canonical

    def _add_canonical(self):
        """ create the cononical for context """
        storage = getUtility(IMultilingualStorage)
        context_id = self.get_id(self.context)
        canonical = Canonical()
        canonical.add_item(ILanguage(self.context).get_language(), context_id)
        storage.add_canonical(context_id, canonical)
        return canonical

    def query_canonical(self):
        canonical = self._get_canonical()
        return canonical

    def register_translation(self, language, content):
        """ register a translation for an existing content """
        if not language and language != '':
            raise KeyError('There is no target language')
        canonical = self._get_or_create()
        if type(content) == str:
            content_id = content
        else:
            content_id = self.get_id(content)

        # register the new translation in the canonical
        canonical.add_item(language, content_id)

        # register the canonical for the translated object
        storage = getUtility(IMultilingualStorage)
        storage.add_canonical(content_id, canonical)
        return

    def update(self):
        """ see interfaces"""
        language = ILanguage(self.context).get_language()
        # In case language is already on the translated languages we are going to orphan the old translation
        if language not in self.get_translated_languages():
            canonical = self._get_or_create()
            content_id = self.get_id(self.context)
            canonical.remove_item_by_id(content_id)
            canonical.add_item(language, content_id)
        else:
            # We need to check if the language has changed
            canonical = self._get_or_create()
            content_id = self.get_id(self.context)
            if canonical.get_item(language) != content_id:
                # Is a different object -> remove the old one
                # We get the old uuid
                uuid_old_translation = canonical.get_item(language)
                # Remove from the storage
                storage = getUtility(IMultilingualStorage)
                storage.remove_canonical(uuid_old_translation)
                # Add the new one
                content_id = self.get_id(self.context)
                canonical.remove_item_by_id(content_id)
                canonical.remove_item_by_id(uuid_old_translation)
                canonical.add_item(language, content_id)
                # Register the new canonical
                new_canonical = Canonical()
                new_canonical.add_item(language, uuid_old_translation)
                storage.add_canonical(uuid_old_translation, new_canonical)

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
        translated_id = self.get_id(translated_object)
        self.register_translation(language, translated_id)
        # event
        notify(ObjectTranslatedEvent(self.context, \
            translated_object, language))
        return

    def remove_translation(self, language):
        """ see interfaces """
        canonical = self._get_canonical()
        if canonical is not None:
            translated_id = canonical.get_item(language)
            # remove language from canonical
            canonical.remove_item_by_language(language)
            # unregister the canonical for the translated object
            storage = getUtility(IMultilingualStorage)
            storage.remove_canonical(translated_id)

    def get_translation(self, language):
        """ see interfaces """
        translation = None
        canonical = self._get_canonical()
        if canonical is not None:
            translation = uuidToObject(canonical.get_item(language))
        return translation

    def get_translations(self):
        """ see interfaces """
        translations = {}
        canonical = self._get_canonical()
        if canonical is not None:
            for language, content_id in canonical.get_items():
                translations[language] = uuidToObject(content_id)
        return translations

    def get_translated_languages(self):
        """ see interfaces """
        languages = []
        canonical = self._get_or_create()
        if canonical is not None:
            languages = canonical.get_keys()
        return languages

    def has_translation(self, language):
        """ see interfaces """
        return language in self.get_translated_languages()
