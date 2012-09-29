# -*- coding: utf-8 -*-
from zope.interface import implements
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from plone.multilingual.interfaces import IMultilingualStorage


class CanonicalStorage(SimpleItem):

    implements(IMultilingualStorage)
    id = 'portal_multilingual'

    def __init__(self):
        self.id = id
        self.canonicals = OOBTree()

    def get_canonical(self, id):
        """ get a canonical for a specific content-id """
        canonical = None
        if id in self.canonicals:
            canonical = self.canonicals[id]
        return canonical

    def add_canonical(self, id, canonical):
        """ add a canonical
            there is a usecase where the id can already exist on the OOBTree
        """
        if not self.canonicals.insert(id, canonical):
            # We are going to remove the language on a old canonical
            # so we need to check if the canonical has other translation active
            # before removing it
            canonical_old = self.get_canonical(id)
            # check if there more than one language on the canonical
            if len(canonical_old.get_keys()) > 1:
                canonical_old.remove_item_by_id(id)
                self.remove_canonical(id)
            else:
                self.remove_canonical(id)
                del canonical_old
                # import transaction; transaction.commit()
            self.canonicals.insert(id, canonical)

    def remove_canonical(self, id):
        """ remove a canonical """
        self.canonicals.pop(id)

    def get_canonicals(self):
        """ get all canonicals """
        return self.canonicals
