import CompositeParamType

class Tuple(CompositeParamType):
    """The default behavior of Click is to apply a type on a value directly.
    This works well in most cases, except for when `nargs` is set to a fixed
    count and different types should be used for different items.  In this
    case the :class:`Tuple` type can be used.  This type can only be used
    if `nargs` is set to a fixed number.

    For more information see :ref:`tuple-type`.

    This can be selected by using a Python tuple literal as a type.

    :param types: a list of types that should be used for the tuple items.
    """

    def __init__(self, types):
        self.types = [convert_type(ty) for ty in types]

    @property
    def name(self):
        return "<" + " ".join(ty.name for ty in self.types) + ">"

    @property
    def arity(self):
        return len(self.types)

    def convert(self, value, param, ctx):
        if len(value) != len(self.types):
            raise TypeError('It would appear that nargs is set to conflict '
                            'with the composite type arity.')
        return tuple(ty(x, param, ctx) for ty, x in zip(self.types, value))
