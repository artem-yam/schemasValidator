from outputMessage import MessageType
from outputMessage import OutputMessage


class JsonObjectValidator(object):
    NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание типа'

    def __init__(self):
        super().__init__()

    def validate(self, jsonObject):
        validationResult = []

        if not jsonObject.description:
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult
