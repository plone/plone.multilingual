from zope.interface import Interface, Attribute


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
