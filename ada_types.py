from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter


class AdaObject(tuple):
    'AdaObject(reads,writes,)'

    __slots__ = ()

    _fields = ('reads', 'writes')

    def __new__(_cls, reads, writes):
        'Create new instance of AdaObject(reads, writes)'
        return _tuple.__new__(_cls, (reads, writes))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AdaObject object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 2:
            raise TypeError('Expected 2 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'AdaObject(reads=%r, writes=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        result = _self._make(map(kwds.pop, ('reads', 'writes'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = _property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    reads = _property(_itemgetter(0), doc='Alias for field number 0')

    writes = _property(_itemgetter(1), doc='Alias for field number 1')


class AdaCallable(tuple):
    'AdaCallable(calls,)'

    __slots__ = ()

    _fields = ('calls',)

    def __new__(_cls, calls,):
        'Create new instance of AdaCallable(calls,)'
        return _tuple.__new__(_cls, (calls,))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AdaCallable object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 1:
            raise TypeError('Expected 1 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'AdaCallable(calls=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        result = _self._make(map(kwds.pop, ('calls',), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = _property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    calls = _property(_itemgetter(0), doc='Alias for field number 0')
