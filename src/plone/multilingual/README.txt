# vim: set ft=rst
==================
plone.multilingual
==================
Idea:

    canonical:
        * the canonical organizes the information about a "translation-group"
        * it's using a dictionary with language-codes as keys and intids as
          values

    storage:
        * persistent storage, which holds the canonicals in an IOBTree
        * the IOBTree's key is the intid of the content, the according value is the canonical

    manager:
        * adapter for ITranslatable
        * provides the API to manage the translations

    adapters:
        * ITranslationLocator - where to put a translation
        * ITranslationIdChooser - generates a valid id for a translation
        * ITranslationCloner - copy the language-independent content to the translation
        * ITranslationFactory - creates the translation

In order to have a test we have a type called Demo that has an adapter
called DemoLanguage that will allow to get the language of the object::

    >>> from plone.multilingual.tests._testing import Demo
    >>> from plone.multilingual.interfaces import ITranslationManager
    >>> from plone.multilingual.interfaces import ILanguage

    >>> portal = layer['portal']

    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectAddedEvent
    >>> notify(ObjectAddedEvent(portal['ob1']))

We create a new translation in 'en' language::

   >>> ITranslationManager(portal['ob1']).add_translation('en')

We try to create a new translation in 'ca' that already exists::

    >>> ITranslationManager(portal['ob1']).add_translation('ca')
    Traceback (most recent call last):
    ...
    KeyError: 'Translation already exists'

We try to create a new translation without language::

    >>> ITranslationManager(portal['ob1']).add_translation(None)
    Traceback (most recent call last):
    ...
    KeyError: 'There is no target language'

We get the 'en' translation::

    >>> ITranslationManager(portal['ob1']).get_translation('en')
    <Demo en ob1-en>
    >>> ILanguage(ITranslationManager(portal['ob1']).get_translation('en')).get_language() == 'en'
    True

let's get all the translations::

    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <Demo ca ob1>, 'en': <Demo en ob1-en>}

let's get only the languages::

    >>> ITranslationManager(portal['ob1']).get_translated_languages()
    ['ca', 'en']

has_translation::

    >>> ITranslationManager(portal['ob1']).has_translation('en')
    True

    >>> ITranslationManager(portal['ob1']).has_translation('it')
    False

register_translation with invalid language::

    >>> ITranslationManager(portal['ob1']).remove_translation('en')
    >>> ITranslationManager(portal['ob1']).register_translation('', portal['ob1-en'])
    Traceback (most recent call last):
    ...
    KeyError: 'There is no target language'

register a translation with content::

    >>> ITranslationManager(portal['ob1']).register_translation('en', portal['ob1-en'])
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <Demo ca ob1>, 'en': <Demo en ob1-en>}

changing the content-language (there should act a subscriber)::

    >>> ILanguage(portal['ob1-en']).set_language('it')
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> notify(ObjectModifiedEvent(portal['ob1-en']))
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <Demo ca ob1>, 'it': <Demo it ob1-en>}

test the delete-subscriber::

    >>> from OFS.event import ObjectWillBeRemovedEvent
    >>> notify(ObjectWillBeRemovedEvent(ITranslationManager(portal['ob1']).get_translation('it')))
    >>> ITranslationManager(portal['ob1']).get_translations()
    {'ca': <Demo ca ob1>}

Default-Adapters
----------------
id-chooser::

    >>> from plone.multilingual.interfaces import ITranslationIdChooser
    >>> chooser = ITranslationIdChooser(portal['ob1-en'])
    >>> chooser(portal, 'es')
    'ob1-es'

locator::

    >>> ITranslationManager(portal['ob1']).add_translation('es')
    >>> child_id = portal.ob1.invokeFactory(type_name='Demo', id="ob1_child", language="ca")

    >>> from plone.multilingual.interfaces import ITranslationLocator
    >>> locator = ITranslationLocator(portal['ob1-en'])
    >>> locator('es') == portal
    True

    >>> child_locator = ITranslationLocator(portal.ob1.ob1_child)
    >>> child_locator('es') == portal['ob1-es']
    True

    >>> ITranslationManager(portal['ob1']).remove_translation('es')

uninstall-profile
-----------------
::

    >>> from plone.app.testing import applyProfile
    >>> applyProfile(portal, 'plone.multilingual:uninstall')

we shouldn't find the storage-utility anymore::

    >>> from plone.multilingual.interfaces import ICanonicalStorage
    >>> gsm = portal.getSiteManager()
    >>> gsm.queryUtility(ICanonicalStorage) == None
    True

