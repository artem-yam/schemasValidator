class OutputMessage:
    def __init__(self, relatedJsonObject, msgType, msgContent):
        self.relatedJsonObject = relatedJsonObject
        self.msgType = msgType
        self.msgContent = msgContent

    def __str__(self) -> str:
        returnString = '{' \
                       '\nТип сообщения: ' + self.msgType + \
                       '\nЭлемент: ' + self.relatedJsonObject.name + \
                       '\nТекст сообщения: ' + self.msgContent + \
                       '\n}\n'

        return returnString


class MessageType:
    INFO_TYPE = 'Информация'
    ERROR_TYPE = 'Ошибка'
