"""An index of all nodes known.

The purpose of this is to be able to
"""


class Repository(object):

    def __init__(self):
        self.store = {}
        # The store. keys: (filename, start sloc, kind name), values: node

    def get_unique_object(self, node):
        ref_tuple = (node.unit.filename, node.sloc_range.start, node.kind_name)
        if ref_tuple in self.store:
            return self.store[ref_tuple]
        else:
            self.store[ref_tuple] = node
            return node
