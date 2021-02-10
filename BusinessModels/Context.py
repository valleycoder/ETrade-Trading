from BusinessUtils.AppLogger import AppLogger


class Context:
    """ Any standard objects passed to most of the class objects.

        Attributes:

        AppLogger - Logger used to log application data/messages.

    """

    def __init__(self, logger:AppLogger):
        self.AppLogger = logger
