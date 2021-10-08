class OutputMessage:
    def __init__(self, relatedJsonObject, msgType, msgContent):
        self.relatedJsonObject = relatedJsonObject
        self.msgType = msgType
        self.msgContent = msgContent

    def __str__(self) -> str:
        returnString = '{\nТип сообщения: ' + self.msgType

        if self.relatedJsonObject:
            if self.relatedJsonObject.fullPath:
                returnString += '\nЭлемент: ' + self.relatedJsonObject.fullPath
            else:
                returnString += '\nЭлемент: ' + self.relatedJsonObject.name

        returnString += '\nТекст сообщения: ' + self.msgContent + '\n}'

        return returnString


class MessageType:
    INFO_TYPE = 'Информация'
    ERROR_TYPE = 'Ошибка'
