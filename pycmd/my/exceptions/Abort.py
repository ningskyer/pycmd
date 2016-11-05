import RuntimeError

class Abort(RuntimeError):
    """An internal signalling exception that signals Click to abort."""
