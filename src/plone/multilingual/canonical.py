from zope.container.contained import Contained
from zope.interface import implements
from persistent import Persistent
from persistent.dict import PersistentDict
from plone.multilingual.interfaces import ICanonical


class Canonical(Persistent, Contained):
    """
    Canonical object that is stored on the Canonicals-Storage
    """
    implements(ICanonical)

    @property
    def languages(self):
        if getattr(self, '_languages', None) is None:
            self._languages = PersistentDict()
        return self._languages

    def add_item(self, language, id):
        if language in self.languages.keys():
            raise KeyError("Translation already exists")
        if not language and language!='':
            raise KeyError("There is no target language")
        self.languages[language] = id

    def remove_item_by_language(self, language):
        if language in self.languages.keys():
            del self.languages[language]

    def remove_item_by_id(self, id):
        language = None
        for item_language, item_id in self.languages.items():
            if item_id == id:
                language = item_language
                break
        if language is not None:
            del(self.languages[language])

    def get_item(self, language):
        item = None
        if language in self.languages.keys():
            item = self.languages[language]
        return item

    def get_items(self):
        return self.languages.items()

    def get_keys(self):
        return self.languages.keys()
