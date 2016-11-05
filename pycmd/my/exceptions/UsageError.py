import BaseException

class UsageError(BaseException):
    """An internal exception that signals a usage error.  This typically
    aborts any further handling.

    :param message: the error message to display.
    :param ctx: optionally the context that caused this error.  Click will
                fill in the context automatically in some situations.
    """
    exit_code = 2

    def __init__(self, message, ctx=None):
        BaseException.__init__(self, message)
        self.ctx = ctx

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
            echo(self.ctx.get_usage() + '\n', file=file, color=color)
        echo('Error: %s' % self.format_message(), file=file, color=color)
