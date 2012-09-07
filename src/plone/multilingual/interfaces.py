from zope.interface import Interface, Attribute


# CONSTANTS
LANGUAGE_INDEPENDENT = ''


# Language-support
class ILanguage(Interface):

    def get_language(self):
        """ return the contents language """

    def set_language(self):
        """ return the contents language """


# Marker interface
class ITranslatable(Interface):
    """Marker interface for content types that support translation"""


# adapters
class ITranslationFactory(Interface):
    """Adapts ITranslated and is capable of returning
       a translation clone to be added.
    """

    def __call__(language):
        """Create a clone of the context
           for translation to the given language
        """


class ITranslationLocator(Interface):
    """Find a parent folder for a translation.
       Adapts ITranslated.
    """

    def __call__(language):
        """Return a parent folder into which a new translation can be added"""


class ITranslationIdChooser(Interface):
    """Find a valid id for a translation
       Adapts ITranslated.
    """

    def __call__(parent, language):
        """ Return a valid id for the translation """


class ITranslationCloner(Interface):
    """Subscription adapters to perform various aspects of cloning an object.
       Allows componentisation of things like workflow history cloning.
       Adapts ITranslated.
    """

    def __call__(object):
        """Update the translation copy that is being constructed"""


class ICanonical(Interface):

    languages = Attribute(u"dictionary {LANG_KEY: UUID, ...}")

    def add_item(language, intid):
        """ """

    def remove_item(language):
        """ """

    def get_item(language):
        """ """

    def remove_item_by_language(language):
        """ """

    def remove_item_by_id(id):
        """ """

    def get_items():
        """ """

    def get_keys():
        """ """


class ITranslationManager(Interface):

    def add_translation(object, intid):
        """
        create the translated content and register the translation
        """

    def remove_translation(language):
        """
        remove translation if exists (unregister the translation)
        """

    def get_translation(language):
        """
        get translation (translated object) if exists
        """

    def get_translations():
        """
        get all the translated objects (including the context)
        """

    def get_translated_languages():
        """
        get a list of the translated languages
        (language-code like 'en', 'it' etc. )
        """

    def register_translation(language, content):
        """
        register an existing content as translation
        for context
        """

    def update():
        """
        update the item registered in the canonical
        (used for changing the contexts language)
        """

    def query_canonical():
        """
        query if there is an canonical for the context
        used for migration
        """


class IMultilingualStorage(Interface):
    """ Stores the canonical objects at the portal_multilingual tool """

    def add_canonical(id, canonical):
        """ add canonical """

    def get_canonical(id):
        """ get canonical """

    def remove_canonical(id):
        """ remove canonical """

    def get_canonicals():
        """ get all canonicals """


class ICanonicalStorage(Interface):
    """ Deprecated in 0.2, for migration purposes only """

    def add_canonical(id, canonical):
        """ add canonical """

    def get_canonical(id):
        """ get canonical """

    def remove_canonical(id):
        """ remove canonical """


class ILanguageIndependentFieldsManager(Interface):
    context = Attribute("context", "A translatable object")

    def copy_fields(translation):
        """ Copy language independent fields to translation."""
