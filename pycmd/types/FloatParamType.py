import BaseParamType

class FloatParamType(BaseParamType):
    name = 'float'

    def convert(self, value, param, ctx):
        try:
            return float(value)
        except (UnicodeError, ValueError):
            self.fail('%s is not a valid floating point value' %
                      value, param, ctx)

    def __repr__(self):
        return 'FLOAT'
