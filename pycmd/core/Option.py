import Parameter

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
