import UsageError

class BadArgumentUsage(UsageError):
    """Raised if an argument is generally supplied but the use of the argument
    was incorrect.  This is for instance raised if the number of values
    for an argument is not correct.

    .. versionadded:: 6.0
    """

    def __init__(self, message, ctx=None):
        UsageError.__init__(self, message, ctx)

