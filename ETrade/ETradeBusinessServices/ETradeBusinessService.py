from BusinessModels.Message import MessageType


class ETradeBusinessService:
    def __init__():
        pass

    def ParseMessageType(self, messageTypeString:str):

        if(messageTypeString == "INFO"):
            return MessageType.INFO
        elif(messageTypeString == "WARNING"):
            return MessageType.WARNING
        elif(messageTypeString == "ERROR"):
            return MessageType.ERROR
        elif(messageTypeString == "INFO_HOLD"):
            return MessageType.INFO_HOLD
        elif(messageTypeString == "FATAL"):
            return MessageType.FATAL
        
        raise Exception(f"Unsupported ETrade Message Type.")
