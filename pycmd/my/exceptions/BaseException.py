

class BaseException(Exception):
    """An exception that Click can handle and show to the user."""

    #: The exit code for this exception
    exit_code = 1

    def __init__(self, message):
        if PY2:
            if message is not None:
                message = message.encode('utf-8')
        Exception.__init__(self, message)
        self.message = message

    def format_message(self):
        return self.message

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        echo('Error: %s' % self.format_message(), file=file)
