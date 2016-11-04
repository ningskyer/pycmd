import Command

class MultiCommand(Command):
    """A multi command is the basic implementation of a command that
    dispatches to subcommands.  The most common version is the
    :class:`Group`.

    :param invoke_without_command: this controls how the multi command itself
                                   is invoked.  By default it's only invoked
                                   if a subcommand is provided.
    :param no_args_is_help: this controls what happens if no arguments are
                            provided.  This option is enabled by default if
                            `invoke_without_command` is disabled or disabled
                            if it's enabled.  If enabled this will add
                            ``--help`` as argument if no arguments are
                            passed.
    :param subcommand_metavar: the string that is used in the documentation
                               to indicate the subcommand place.
    :param chain: if this is set to `True` chaining of multiple subcommands
                  is enabled.  This restricts the form of commands in that
                  they cannot have optional arguments but it allows
                  multiple commands to be chained together.
    :param result_callback: the result callback to attach to this multi
                            command.
    """
    allow_extra_args = True
    allow_interspersed_args = False

    def __init__(self, name=None, invoke_without_command=False,
                 no_args_is_help=None, subcommand_metavar=None,
                 chain=False, result_callback=None, **attrs):
        Command.__init__(self, name, **attrs)
        if no_args_is_help is None:
            no_args_is_help = not invoke_without_command
        self.no_args_is_help = no_args_is_help
        self.invoke_without_command = invoke_without_command
        if subcommand_metavar is None:
            if chain:
                subcommand_metavar = SUBCOMMANDS_METAVAR
            else:
                subcommand_metavar = SUBCOMMAND_METAVAR
        self.subcommand_metavar = subcommand_metavar
        self.chain = chain
        #: The result callback that is stored.  This can be set or
        #: overridden with the :func:`resultcallback` decorator.
        self.result_callback = result_callback

        if self.chain:
            for param in self.params:
                if isinstance(param, Argument) and not param.required:
                    raise RuntimeError('Multi commands in chain mode cannot '
                                       'have optional arguments.')

    def collect_usage_pieces(self, ctx):
        rv = Command.collect_usage_pieces(self, ctx)
        rv.append(self.subcommand_metavar)
        return rv

    def format_options(self, ctx, formatter):
        Command.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)

    def resultcallback(self, replace=False):
        """Adds a result callback to the chain command.  By default if a
        result callback is already registered this will chain them but
        this can be disabled with the `replace` parameter.  The result
        callback is invoked with the return value of the subcommand
        (or the list of return values from all subcommands if chaining
        is enabled) as well as the parameters as they would be passed
        to the main callback.

        Example::

            @click.group()
            @click.option('-i', '--input', default=23)
            def cli(input):
                return 42

            @cli.resultcallback()
            def process_result(result, input):
                return result + input

        .. versionadded:: 3.0

        :param replace: if set to `True` an already existing result
                        callback will be removed.
        """
        def decorator(f):
            old_callback = self.result_callback
            if old_callback is None or replace:
                self.result_callback = f
                return f
            def function(__value, *args, **kwargs):
                return f(old_callback(__value, *args, **kwargs),
                         *args, **kwargs)
            self.result_callback = rv = update_wrapper(function, f)
            return rv
        return decorator

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        rows = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue

            help = cmd.short_help or ''
            rows.append((subcommand, help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)

    def parse_args(self, ctx, args):
        if not args and self.no_args_is_help and not ctx.resilient_parsing:
            echo(ctx.get_help(), color=ctx.color)
            ctx.exit()

        rest = Command.parse_args(self, ctx, args)
        if self.chain:
            ctx.protected_args = rest
            ctx.args = []
        elif rest:
            ctx.protected_args, ctx.args = rest[:1], rest[1:]

        return ctx.args

    def invoke(self, ctx):
        def _process_result(value):
            if self.result_callback is not None:
                value = ctx.invoke(self.result_callback, value,
                                   **ctx.params)
            return value

        if not ctx.protected_args:
            # If we are invoked without command the chain flag controls
            # how this happens.  If we are not in chain mode, the return
            # value here is the return value of the command.
            # If however we are in chain mode, the return value is the
            # return value of the result processor invoked with an empty
            # list (which means that no subcommand actually was executed).
            if self.invoke_without_command:
                if not self.chain:
                    return Command.invoke(self, ctx)
                with ctx:
                    Command.invoke(self, ctx)
                    return _process_result([])
            ctx.fail('Missing command.')

        # Fetch args back out
        args = ctx.protected_args + ctx.args
        ctx.args = []
        ctx.protected_args = []

        # If we're not in chain mode, we only allow the invocation of a
        # single command but we also inform the current context about the
        # name of the command to invoke.
        if not self.chain:
            # Make sure the context is entered so we do not clean up
            # resources until the result processor has worked.
            with ctx:
                cmd_name, cmd, args = self.resolve_command(ctx, args)
                ctx.invoked_subcommand = cmd_name
                Command.invoke(self, ctx)
                sub_ctx = cmd.make_context(cmd_name, args, parent=ctx)
                with sub_ctx:
                    return _process_result(sub_ctx.command.invoke(sub_ctx))

        # In chain mode we create the contexts step by step, but after the
        # base command has been invoked.  Because at that point we do not
        # know the subcommands yet, the invoked subcommand attribute is
        # set to ``*`` to inform the command that subcommands are executed
        # but nothing else.
        with ctx:
            ctx.invoked_subcommand = args and '*' or None
            Command.invoke(self, ctx)

            # Otherwise we make every single context and invoke them in a
            # chain.  In that case the return value to the result processor
            # is the list of all invoked subcommand's results.
            contexts = []
            while args:
                cmd_name, cmd, args = self.resolve_command(ctx, args)
                sub_ctx = cmd.make_context(cmd_name, args, parent=ctx,
                                           allow_extra_args=True,
                                           allow_interspersed_args=False)
                contexts.append(sub_ctx)
                args, sub_ctx.args = sub_ctx.args, []

            rv = []
            for sub_ctx in contexts:
                with sub_ctx:
                    rv.append(sub_ctx.command.invoke(sub_ctx))
            return _process_result(rv)

    def resolve_command(self, ctx, args):
        cmd_name = make_str(args[0])
        original_cmd_name = cmd_name

        # Get the command
        cmd = self.get_command(ctx, cmd_name)

        # If we can't find the command but there is a normalization
        # function available, we try with that one.
        if cmd is None and ctx.token_normalize_func is not None:
            cmd_name = ctx.token_normalize_func(cmd_name)
            cmd = self.get_command(ctx, cmd_name)

        # If we don't find the command we want to show an error message
        # to the user that it was not provided.  However, there is
        # something else we should do: if the first argument looks like
        # an option we want to kick off parsing again for arguments to
        # resolve things like --help which now should go to the main
        # place.
        if cmd is None:
            if split_opt(cmd_name)[0]:
                self.parse_args(ctx, ctx.args)
            ctx.fail('No such command "%s".' % original_cmd_name)

        return cmd_name, cmd, args[1:]

    def get_command(self, ctx, cmd_name):
        """Given a context and a command name, this returns a
        :class:`Command` object if it exists or returns `None`.
        """
        raise NotImplementedError()

    def list_commands(self, ctx):
        """Returns a list of subcommand names in the order they should
        appear.
        """
        return []
