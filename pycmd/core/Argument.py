import Parameter

class Argument(Parameter):
    """Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    All parameters are passed onwards to the parameter constructor.
    """
    param_type_name = 'argument'

    def __init__(self, param_decls, required=None, **attrs):
        if required is None:
            if attrs.get('default') is not None:
                required = False
            else:
                required = attrs.get('nargs', 1) > 0
        Parameter.__init__(self, param_decls, required=required, **attrs)
        if self.default is not None and self.nargs < 0:
            raise TypeError('nargs=-1 in combination with a default value '
                            'is not supported.')

    @property
    def human_readable_name(self):
        if self.metavar is not None:
            return self.metavar
        return self.name.upper()

    def make_metavar(self):
        if self.metavar is not None:
            return self.metavar
        var = self.name.upper()
        if not self.required:
            var = '[%s]' % var
        if self.nargs != 1:
            var += '...'
        return var

    def _parse_decls(self, decls, expose_value):
        if not decls:
            if not expose_value:
                return None, [], []
            raise TypeError('Could not determine name for argument')
        if len(decls) == 1:
            name = arg = decls[0]
            name = name.replace('-', '_').lower()
        elif len(decls) == 2:
            name, arg = decls
        else:
            raise TypeError('Arguments take exactly one or two '
                            'parameter declarations, got %d' % len(decls))
        return name, [arg], []

    def get_usage_pieces(self, ctx):
        return [self.make_metavar()]

    def add_to_parser(self, parser, ctx):
        parser.add_argument(dest=self.name, nargs=self.nargs,
                            obj=self)
