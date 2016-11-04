import BadParameter

class MissingParameter(BadParameter):
    """Raised if click required an option or argument but it was not
    provided when invoking the script.

    .. versionadded:: 4.0

    :param param_type: a string that indicates the type of the parameter.
                       The default is to inherit the parameter type from
                       the given `param`.  Valid values are ``'parameter'``,
                       ``'option'`` or ``'argument'``.
    """

    def __init__(self, message=None, ctx=None, param=None,
                 param_hint=None, param_type=None):
        BadParameter.__init__(self, message, ctx, param, param_hint)
        self.param_type = param_type

    def format_message(self):
        if self.param_hint is not None:
            param_hint = self.param_hint
        elif self.param is not None:
            param_hint = self.param.opts or [self.param.human_readable_name]
        else:
            param_hint = None
        if isinstance(param_hint, (tuple, list)):
            param_hint = ' / '.join('"%s"' % x for x in param_hint)

        param_type = self.param_type
        if param_type is None and self.param is not None:
            param_type = self.param.param_type_name

        msg = self.message
        if self.param is not None:
            msg_extra = self.param.type.get_missing_message(self.param)
            if msg_extra:
                if msg:
                    msg += '.  ' + msg_extra
                else:
                    msg = msg_extra

        return 'Missing %s%s%s%s' % (
            param_type,
            param_hint and ' %s' % param_hint or '',
            msg and '.  ' or '.',
            msg or '',
        )