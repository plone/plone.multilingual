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
        """ add a canonical """
        self.canonicals.insert(id, canonical)

    def remove_canonical(self, id):
        """ remove a canonical """
        self.canonicals.pop(id)
