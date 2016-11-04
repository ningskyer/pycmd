import BaseException

class FileExistsError(BaseException):
    """Raised if a file exists already."""

    def __init__(self, filename, hint=None):
        ui_filename = filename_to_ui(filename)
        if hint is None:
            hint = 'unknown error'
        BaseException.__init__(self, hint)
        self.ui_filename = ui_filename
        self.filename = filename

    def format_message(self):
        return 'file name %s exists' % (self.ui_filename)

