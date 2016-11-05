from .multiCommand import MultiCommand

class CommandCollection(MultiCommand):
    """A command collection is a multi command that merges multiple multi
    commands together into one.  This is a straightforward implementation
    that accepts a list of different multi commands as sources and
    provides all the commands for each of them.
    """

    def __init__(self, name=None, sources=None, **attrs):
        MultiCommand.__init__(self, name, **attrs)
        #: The list of registered multi commands.
        self.sources = sources or []

    def add_source(self, multi_cmd):
        """Adds a new multi command to the chain dispatcher."""
        self.sources.append(multi_cmd)

    def get_command(self, ctx, cmd_name):
        for source in self.sources:
            rv = source.get_command(ctx, cmd_name)
            if rv is not None:
                if self.chain:
                    _check_multicommand(self, cmd_name, rv)
                return rv

    def list_commands(self, ctx):
        rv = set()
        for source in self.sources:
            rv.update(source.list_commands(ctx))
        return sorted(rv)
