import BaseParamType

class UUIDParameterType(BaseParamType):
    name = 'uuid'

    def convert(self, value, param, ctx):
        import uuid
        try:
            if PY2 and isinstance(value, text_type):
                value = value.encode('ascii')
            return uuid.UUID(value)
        except (UnicodeError, ValueError):
            self.fail('%s is not a valid UUID value' % value, param, ctx)

    def __repr__(self):
        return 'UUID'

