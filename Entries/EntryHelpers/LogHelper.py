from BusinessUtils.AppLogger import AppLogger


def LogMessage(logger:AppLogger, message:str, isError:bool = False, isDisplay:bool = False):
    """ Log Message Helper function. 

        Parameters:

        logger:AppLogger - AppLogger encapsulating the Logger.

        message:str - Message to log.

        isError:bool - Is error or other type of message.

        isDisplay:bool - Is the message need to be displayed to console.

    """

    # If IsDisplay print the message.
    if isDisplay is True:
        print(message)
    if(logger is not None and logger.Logger is not None):
        if isError is True:
            logger.Logger.error(message)
        else:
            logger.Logger.info(message)
