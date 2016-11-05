from ..cmdtypes import convert_type, IntRange, BOOL

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


class Option(Parameter):
    """Options are usually optional values on the command line and
    have some extra features that arguments don't have.

    All other parameters are passed onwards to the parameter constructor.

    :param show_default: controls if the default value should be shown on the
                         help page.  Normally, defaults are not shown.
    :param prompt: if set to `True` or a non empty string then the user will
                   be prompted for input if not set.  If set to `True` the
                   prompt will be the option name capitalized.
    :param confirmation_prompt: if set then the value will need to be confirmed
                                if it was prompted for.
    :param hide_input: if this is `True` then the input on the prompt will be
                       hidden from the user.  This is useful for password
                       input.
    :param is_flag: forces this option to act as a flag.  The default is
                    auto detection.
    :param flag_value: which value should be used for this flag if it's
                       enabled.  This is set to a boolean automatically if
                       the option string contains a slash to mark two options.
    :param multiple: if this is set to `True` then the argument is accepted
                     multiple times and recorded.  This is similar to ``nargs``
                     in how it works but supports arbitrary number of
                     arguments.
    :param count: this flag makes an option increment an integer.
    :param allow_from_autoenv: if this is enabled then the value of this
                               parameter will be pulled from an environment
                               variable in case a prefix is defined on the
                               context.
    :param help: the help string.
    """
    param_type_name = 'option'

    def __init__(self, param_decls=None, show_default=False,
                 prompt=False, confirmation_prompt=False,
                 hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True,
                 type=None, help=None, **attrs):
        default_is_missing = attrs.get('default', _missing) is _missing
        Parameter.__init__(self, param_decls, type=type, **attrs)

        if prompt is True:
            prompt_text = self.name.replace('_', ' ').capitalize()
        elif prompt is False:
            prompt_text = None
        else:
            prompt_text = prompt
        self.prompt = prompt_text
        self.confirmation_prompt = confirmation_prompt
        self.hide_input = hide_input

        # Flags
        if is_flag is None:
            if flag_value is not None:
                is_flag = True
            else:
                is_flag = bool(self.secondary_opts)
        if is_flag and default_is_missing:
            self.default = False
        if flag_value is None:
            flag_value = not self.default
        self.is_flag = is_flag
        self.flag_value = flag_value
        if self.is_flag and isinstance(self.flag_value, bool) \
           and type is None:
            self.type = BOOL
            self.is_bool_flag = True
        else:
            self.is_bool_flag = False

        # Counting
        self.count = count
        if count:
            if type is None:
                self.type = IntRange(min=0)
            if default_is_missing:
                self.default = 0

        self.multiple = multiple
        self.allow_from_autoenv = allow_from_autoenv
        self.help = help
        self.show_default = show_default

        # Sanity check for stuff we don't support
        if __debug__:
            if self.nargs < 0:
                raise TypeError('Options cannot have nargs < 0')
            if self.prompt and self.is_flag and not self.is_bool_flag:
                raise TypeError('Cannot prompt for flags that are not bools.')
            if not self.is_bool_flag and self.secondary_opts:
                raise TypeError('Got secondary option for non boolean flag.')
            if self.is_bool_flag and self.hide_input \
               and self.prompt is not None:
                raise TypeError('Hidden input does not work with boolean '
                                'flag prompts.')
            if self.count:
                if self.multiple:
                    raise TypeError('Options cannot be multiple and count '
                                    'at the same time.')
                elif self.is_flag:
                    raise TypeError('Options cannot be count and flags at '
                                    'the same time.')

    def _parse_decls(self, decls, expose_value):
        opts = []
        secondary_opts = []
        name = None
        possible_names = []

        for decl in decls:
            if isidentifier(decl):
                if name is not None:
                    raise TypeError('Name defined twice')
                name = decl
            else:
                split_char = decl[:1] == '/' and ';' or '/'
                if split_char in decl:
                    first, second = decl.split(split_char, 1)
                    first = first.rstrip()
                    if first:
                        possible_names.append(split_opt(first))
                        opts.append(first)
                    second = second.lstrip()
                    if second:
                        secondary_opts.append(second.lstrip())
                else:
                    possible_names.append(split_opt(decl))
                    opts.append(decl)

        if name is None and possible_names:
            possible_names.sort(key=lambda x: len(x[0]))
            name = possible_names[-1][1].replace('-', '_').lower()
            if not isidentifier(name):
                name = None

        if name is None:
            if not expose_value:
                return None, opts, secondary_opts
            raise TypeError('Could not determine name for option')

        if not opts and not secondary_opts:
            raise TypeError('No options defined but a name was passed (%s). '
                            'Did you mean to declare an argument instead '
                            'of an option?' % name)

        return name, opts, secondary_opts

    def add_to_parser(self, parser, ctx):
        kwargs = {
            'dest': self.name,
            'nargs': self.nargs,
            'obj': self,
        }

        if self.multiple:
            action = 'append'
        elif self.count:
            action = 'count'
        else:
            action = 'store'

        if self.is_flag:
            kwargs.pop('nargs', None)
            if self.is_bool_flag and self.secondary_opts:
                parser.add_option(self.opts, action=action + '_const',
                                  const=True, **kwargs)
                parser.add_option(self.secondary_opts, action=action +
                                  '_const', const=False, **kwargs)
            else:
                parser.add_option(self.opts, action=action + '_const',
                                  const=self.flag_value,
                                  **kwargs)
        else:
            kwargs['action'] = action
            parser.add_option(self.opts, **kwargs)

    def get_help_record(self, ctx):
        any_prefix_is_slash = []

        def _write_opts(opts):
            rv, any_slashes = join_options(opts)
            if any_slashes:
                any_prefix_is_slash[:] = [True]
            if not self.is_flag and not self.count:
                rv += ' ' + self.make_metavar()
            return rv

        rv = [_write_opts(self.opts)]
        if self.secondary_opts:
            rv.append(_write_opts(self.secondary_opts))

        help = self.help or ''
        extra = []
        if self.default is not None and self.show_default:
            extra.append('default: %s' % (
                         ', '.join('%s' % d for d in self.default)
                         if isinstance(self.default, (list, tuple))
                         else self.default, ))
        if self.required:
            extra.append('required')
        if extra:
            help = '%s[%s]' % (help and help + '  ' or '', '; '.join(extra))

        return ((any_prefix_is_slash and '; ' or ' / ').join(rv), help)

    def get_default(self, ctx):
        # If we're a non boolean flag out default is more complex because
        # we need to look at all flags in the same group to figure out
        # if we're the the default one in which case we return the flag
        # value as default.
        if self.is_flag and not self.is_bool_flag:
            for param in ctx.command.params:
                if param.name == self.name and param.default:
                    return param.flag_value
            return None
        return Parameter.get_default(self, ctx)

    def prompt_for_value(self, ctx):
        """This is an alternative flow that can be activated in the full
        value processing if a value does not exist.  It will prompt the
        user until a valid value exists and then returns the processed
        value as result.
        """
        # Calculate the default before prompting anything to be stable.
        default = self.get_default(ctx)

        # If this is a prompt for a flag we need to handle this
        # differently.
        if self.is_bool_flag:
            return confirm(self.prompt, default)

        return prompt(self.prompt, default=default,
                      hide_input=self.hide_input,
                      confirmation_prompt=self.confirmation_prompt,
                      value_proc=lambda x: self.process_value(ctx, x))

    def resolve_envvar_value(self, ctx):
        rv = Parameter.resolve_envvar_value(self, ctx)
        if rv is not None:
            return rv
        if self.allow_from_autoenv and \
           ctx.auto_envvar_prefix is not None:
            envvar = '%s_%s' % (ctx.auto_envvar_prefix, self.name.upper())
            return os.environ.get(envvar)

    def value_from_envvar(self, ctx):
        rv = self.resolve_envvar_value(ctx)
        if rv is None:
            return None
        value_depth = (self.nargs != 1) + bool(self.multiple)
        if value_depth > 0 and rv is not None:
            rv = self.type.split_envvar_value(rv)
            if self.multiple and self.nargs != 1:
                rv = batch(rv, self.nargs)
        return rv

    def full_process_value(self, ctx, value):
        if value is None and self.prompt is not None \
           and not ctx.resilient_parsing:
            return self.prompt_for_value(ctx)
        return Parameter.full_process_value(self, ctx, value)



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
