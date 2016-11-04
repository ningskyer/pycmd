import UsageError

class BadOptionUsage(UsageError):
    """Raised if an option is generally supplied but the use of the option
    was incorrect.  This is for instance raised if the number of arguments
    for an option is not correct.

    .. versionadded:: 4.0
    """

    def __init__(self, message, ctx=None):
        UsageError.__init__(self, message, ctx)

