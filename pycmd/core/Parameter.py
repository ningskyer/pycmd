

class Parameter(object):
    """A parameter to a command comes in two versions: they are either
    :class:`Option`\s or :class:`Argument`\s.  Other subclasses are currently
    not supported by design as some of the internals for parsing are
    intentionally not finalized.

    Some settings are supported by both options and arguments.

    .. versionchanged:: 2.0
       Changed signature for parameter callback to also be passed the
       parameter.  In Click 2.0, the old callback format will still work,
       but it will raise a warning to give you change to migrate the
       code easier.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param type: the type that should be used.  Either a :class:`ParamType`
                 or a Python type.  The later is converted into the former
                 automatically if supported.
    :param required: controls if this is optional or not.
    :param default: the default value if omitted.  This can also be a callable,
                    in which case it's invoked when the default is needed
                    without any arguments.
    :param callback: a callback that should be executed after the parameter
                     was matched.  This is called as ``fn(ctx, param,
                     value)`` and needs to return the value.  Before Click
                     2.0, the signature was ``(ctx, value)``.
    :param nargs: the number of arguments to match.  If not ``1`` the return
                  value is a tuple instead of single value.  The default for
                  nargs is ``1`` (except if the type is a tuple, then it's
                  the arity of the tuple).
    :param metavar: how the value is represented in the help page.
    :param expose_value: if this is `True` then the value is passed onwards
                         to the command callback and stored on the context,
                         otherwise it's skipped.
    :param is_eager: eager values are processed before non eager ones.  This
                     should not be set for arguments or it will inverse the
                     order of processing.
    :param envvar: a string or list of strings that are environment variables
                   that should be checked.
    """
    param_type_name = 'parameter'

    def __init__(self, param_decls=None, type=None, required=False,
                 default=None, callback=None, nargs=None, metavar=None,
                 expose_value=True, is_eager=False, envvar=None):
        self.name, self.opts, self.secondary_opts = \
            self._parse_decls(param_decls or (), expose_value)

        self.type = convert_type(type, default)

        # Default nargs to what the type tells us if we have that
        # information available.
        if nargs is None:
            if self.type.is_composite:
                nargs = self.type.arity
            else:
                nargs = 1

        self.required = required
        self.callback = callback
        self.nargs = nargs
        self.multiple = False
        self.expose_value = expose_value
        self.default = default
        self.is_eager = is_eager
        self.metavar = metavar
        self.envvar = envvar

    @property
    def human_readable_name(self):
        """Returns the human readable name of this parameter.  This is the
        same as the name for options, but the metavar for arguments.
        """
        return self.name

    def make_metavar(self):
        if self.metavar is not None:
            return self.metavar
        metavar = self.type.get_metavar(self)
        if metavar is None:
            metavar = self.type.name.upper()
        if self.nargs != 1:
            metavar += '...'
        return metavar

    def get_default(self, ctx):
        """Given a context variable this calculates the default value."""
        # Otherwise go with the regular default.
        if callable(self.default):
            rv = self.default()
        else:
            rv = self.default
        return self.type_cast_value(ctx, rv)

    def add_to_parser(self, parser, ctx):
        pass

    def consume_value(self, ctx, opts):
        value = opts.get(self.name)
        if value is None:
            value = ctx.lookup_default(self.name)
        if value is None:
            value = self.value_from_envvar(ctx)
        return value

    def type_cast_value(self, ctx, value):
        """Given a value this runs it properly through the type system.
        This automatically handles things like `nargs` and `multiple` as
        well as composite types.
        """
        if self.type.is_composite:
            if self.nargs <= 1:
                raise TypeError('Attempted to invoke composite type '
                                'but nargs has been set to %s.  This is '
                                'not supported; nargs needs to be set to '
                                'a fixed value > 1.' % self.nargs)
            if self.multiple:
                return tuple(self.type(x or (), self, ctx) for x in value or ())
            return self.type(value or (), self, ctx)

        def _convert(value, level):
            if level == 0:
                return self.type(value, self, ctx)
            return tuple(_convert(x, level - 1) for x in value or ())
        return _convert(value, (self.nargs != 1) + bool(self.multiple))

    def process_value(self, ctx, value):
        """Given a value and context this runs the logic to convert the
        value as necessary.
        """
        # If the value we were given is None we do nothing.  This way
        # code that calls this can easily figure out if something was
        # not provided.  Otherwise it would be converted into an empty
        # tuple for multiple invocations which is inconvenient.
        if value is not None:
            return self.type_cast_value(ctx, value)

    def value_is_missing(self, value):
        if value is None:
            return True
        if (self.nargs != 1 or self.multiple) and value == ():
            return True
        return False

    def full_process_value(self, ctx, value):
        value = self.process_value(ctx, value)

        if value is None:
            value = self.get_default(ctx)

        if self.required and self.value_is_missing(value):
            raise MissingParameter(ctx=ctx, param=self)

        return value

    def resolve_envvar_value(self, ctx):
        if self.envvar is None:
            return
        if isinstance(self.envvar, (tuple, list)):
            for envvar in self.envvar:
                rv = os.environ.get(envvar)
                if rv is not None:
                    return rv
        else:
            return os.environ.get(self.envvar)

    def value_from_envvar(self, ctx):
        rv = self.resolve_envvar_value(ctx)
        if rv is not None and self.nargs != 1:
            rv = self.type.split_envvar_value(rv)
        return rv

    def handle_parse_result(self, ctx, opts, args):
        with augment_usage_errors(ctx, param=self):
            value = self.consume_value(ctx, opts)
            try:
                value = self.full_process_value(ctx, value)
            except Exception:
                if not ctx.resilient_parsing:
                    raise
                value = None
            if self.callback is not None:
                try:
                    value = invoke_param_callback(
                        self.callback, ctx, self, value)
                except Exception:
                    if not ctx.resilient_parsing:
                        raise

        if self.expose_value:
            ctx.params[self.name] = value
        return value, args

    def get_help_record(self, ctx):
        pass

    def get_usage_pieces(self, ctx):
        return []

