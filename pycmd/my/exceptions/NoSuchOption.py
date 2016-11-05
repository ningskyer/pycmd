import UsageError

class NoSuchOption(UsageError):
    """Raised if click attempted to handle an option that does not
    exist.

    .. versionadded:: 4.0
    """

    def __init__(self, option_name, message=None, possibilities=None,
                 ctx=None):
        if message is None:
            message = 'no such option: %s' % option_name
        UsageError.__init__(self, message, ctx)
        self.option_name = option_name
        self.possibilities = possibilities

    def format_message(self):
        bits = [self.message]
        if self.possibilities:
            if len(self.possibilities) == 1:
                bits.append('Did you mean %s?' % self.possibilities[0])
            else:
                possibilities = sorted(self.possibilities)
                bits.append('(Possible options: %s)' % ', '.join(possibilities))
        return '  '.join(bits)
