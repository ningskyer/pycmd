import BaseParamType

class IntParamType(BaseParamType):
    name = 'integer'

    def convert(self, value, param, ctx):
        try:
            return int(value)
        except (ValueError, UnicodeError):
            self.fail('%s is not a valid integer' % value, param, ctx)

    def __repr__(self):
        return 'INT'
