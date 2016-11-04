import BaseParamType

class CompositeParamType(BaseParamType):
    is_composite = True

    @property
    def arity(self):
        raise NotImplementedError()

