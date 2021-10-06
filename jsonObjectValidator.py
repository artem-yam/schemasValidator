from outputMessage import MessageType
from outputMessage import OutputMessage


class JsonObjectValidator(object):
    NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание типа'
    NO_MAX_LENGTH_MESSAGE = 'Отсутствует ограничение по длине строки'
    EXCESS_MAX_LENGTH_MESSAGE = 'Указаная максимальная длина строки выше допустимой'

    def __init__(self):
        super().__init__()
        self.allowedStringMaxLength = 10

    def validate(self, jsonObject):
        validationResult = []

        if not jsonObject.description:
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if str(jsonObject.propType).lower() == 'string':
            if jsonObject.extraInfo:
                # print(f'String object {jsonObject} has extraInfo')
                extraInfo = jsonObject.extraInfo
                if 'maxLength' not in extraInfo:
                    # print(f'has max length')
                    validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                                 JsonObjectValidator.NO_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)
                elif self.allowedStringMaxLength and extraInfo['maxLength'] > self.allowedStringMaxLength:
                    # print(f'Max length {extraInfo["maxLength"]} is more then allowed {self.allowedStringMaxLength}')
                    validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                                 JsonObjectValidator.EXCESS_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)

        return validationResult
