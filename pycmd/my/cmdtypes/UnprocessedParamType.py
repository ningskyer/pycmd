import BaseParamType

class UnprocessedParamType(BaseParamType):
    name = 'text'

    def convert(self, value, param, ctx):
        return value

    def __repr__(self):
        return 'UNPROCESSED'

