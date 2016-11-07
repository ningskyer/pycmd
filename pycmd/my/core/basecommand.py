import os, sys

from _compat import iteritems, PY2
from _unicodefun import _verify_python3_env, _check_for_unicode_literals
from utils import get_os_args, make_str, _bashcomplete
from exceptions import Abort, ClickException
from .context import Context

class BaseCommand(object):
    """The base command implements the minimal API contract of commands.
    Most code will never use this as it does not implement a lot of useful
    functionality but it can act as the direct subclass of alternative
    parsing methods that do not depend on the Click parser.

    For instance, this can be used to bridge Click and other systems like
    argparse or docopt.

    Because base commands do not implement a lot of the API that other
    parts of Click take for granted, they are not supported for all
    operations.  For instance, they cannot be used with the decorators
    usually and they have no built-in callback system.

    .. versionchanged:: 2.0
       Added the `context_settings` parameter.

    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    """
    #: the default for the :attr:`Context.allow_extra_args` flag.
    allow_extra_args = False
    #: the default for the :attr:`Context.allow_interspersed_args` flag.
    allow_interspersed_args = True
    #: the default for the :attr:`Context.ignore_unknown_options` flag.
    ignore_unknown_options = False

    def __init__(self, name, context_settings=None):
        #: the name the command thinks it has.  Upon registering a command
        #: on a :class:`Group` the group will default the command name
        #: with this information.  You should instead use the
        #: :class:`Context`\'s :attr:`~Context.info_name` attribute.
        self.name = name
        if context_settings is None:
            context_settings = {}
        #: an optional dictionary with defaults passed to the context.
        self.context_settings = context_settings

    def get_usage(self, ctx):
        raise NotImplementedError('Base commands cannot get usage')

    def get_help(self, ctx):
        raise NotImplementedError('Base commands cannot get help')

    def make_context(self, info_name, args, parent=None, **extra):
        """This function when given an info name and arguments will kick
        off the parsing and create a new :class:`Context`.  It does not
        invoke the actual command callback though.

        :param info_name: the info name for this invokation.  Generally this
                          is the most descriptive name for the script or
                          command.  For the toplevel script it's usually
                          the name of the script, for commands below it it's
                          the name of the script.
        :param args: the arguments to parse as list of strings.
        :param parent: the parent context if available.
        :param extra: extra keyword arguments forwarded to the context
                      constructor.
        """
        for key, value in iteritems(self.context_settings):
            if key not in extra:
                extra[key] = value
        
        ctx = Context(self, info_name=info_name, parent=parent, **extra)
        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        print('after parse_args')
        return ctx

    def parse_args(self, ctx, args):
        """Given a context and a list of arguments this creates the parser
        and parses the arguments, then modifies the context as necessary.
        This is automatically invoked by :meth:`make_context`.
        """
        raise NotImplementedError('Base commands do not know how to parse '
                                  'arguments.')

    def invoke(self, ctx):
        """Given a context, this invokes the command.  The default
        implementation is raising a not implemented error.
        """
        raise NotImplementedError('Base commands are not invokable by default')

    def main(self, args=None, prog_name=None, complete_var=None,
             standalone_mode=True, **extra):
        """This is the way to invoke a script with all the bells and
        whistles as a command line application.  This will always terminate
        the application after a call.  If this is not wanted, ``SystemExit``
        needs to be caught.

        This method is also available by directly calling the instance of
        a :class:`Command`.

        .. versionadded:: 3.0
           Added the `standalone_mode` flag to control the standalone mode.

        :param args: the arguments that should be used for parsing.  If not
                     provided, ``sys.argv[1:]`` is used.
        :param prog_name: the program name that should be used.  By default
                          the program name is constructed by taking the file
                          name from ``sys.argv[0]``.
        :param complete_var: the environment variable that controls the
                             bash completion support.  The default is
                             ``"_<prog_name>_COMPLETE"`` with prog name in
                             uppercase.
        :param standalone_mode: the default behavior is to invoke the script
                                in standalone mode.  Click will then
                                handle exceptions and convert them into
                                error messages and the function will never
                                return but shut down the interpreter.  If
                                this is set to `False` they will be
                                propagated to the caller and the return
                                value of this function is the return value
                                of :meth:`invoke`.
        :param extra: extra keyword arguments are forwarded to the context
                      constructor.  See :class:`Context` for more information.
        """
        # If we are in Python 3, we will verify that the environment is
        # sane at this point of reject further execution to avoid a
        # broken script.
        if not PY2:
            _verify_python3_env()
        else:
            _check_for_unicode_literals()

        if args is None:
            args = get_os_args()
        else:
            args = list(args)

        if prog_name is None:
            prog_name = make_str(os.path.basename(
                sys.argv and sys.argv[0] or __file__))

        # Hook for the Bash completion.  This only activates if the Bash
        # completion is actually enabled, otherwise this is quite a fast
        # noop.
        _bashcomplete(self, prog_name, complete_var)
        try:
            try:
                print("2shittttttttttuuuuuuuuuuu")
                with self.make_context(prog_name, args, **extra) as ctx:
                    print("3shittttttttttuuuuuuuuuuu")

                    rv = self.invoke(ctx)
                    if not standalone_mode:
                        return rv
                    ctx.exit()
            except (EOFError, KeyboardInterrupt):
                print("33333")
                echo(file=sys.stderr)
                raise Abort()
            except ClickException as e:
                print("444444")
                if not standalone_mode:
                    raise
                e.show()
                sys.exit(e.exit_code)
        except Abort:
            print("5555555555")
            if not standalone_mode:
                raise
            echo('Aborted!', file=sys.stderr)
            sys.exit(1)

    def __call__(self, *args, **kwargs):
        """Alias for :meth:`main`."""
        return self.main(*args, **kwargs)
