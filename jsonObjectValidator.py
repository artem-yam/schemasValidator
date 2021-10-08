from outputMessage import MessageType
from outputMessage import OutputMessage


class JsonObjectValidator(object):
    NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание типа'
    NO_MAX_LENGTH_MESSAGE = 'Отсутствует ограничение по длине строки'
    EXCESS_MAX_LENGTH_MESSAGE = 'Указаная максимальная длина строки выше допустимой'
    NO_ARRAY_ITEMS_MESSAGE = 'Для массива не определен блок items'

    DRAFT_4_SHORT_DEFINITION = 'draft-04'
    DRAFT_7_SHORT_DEFINITION = 'draft-07'
    AVAILABLE_DRAFT_VERSIONS_SHORT = [DRAFT_4_SHORT_DEFINITION, DRAFT_7_SHORT_DEFINITION]
    AVAILABLE_DRAFT_VERSIONS = [f'http://json-schema.org/{x}/schema#' for x in AVAILABLE_DRAFT_VERSIONS_SHORT]
    CORRECT_DRAFT_MESSAGE = 'В схеме использована версия драфта: '
    INCORRECT_DRAFT_MESSAGE = 'В схеме использована некорректная версия драфта: '

    def __init__(self):
        super().__init__()
        self.allowedStringMaxLength = 0

    def validate(self, jsonObject):
        validationResult = []

        if not jsonObject.description:
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if jsonObject.propType == 'string':
            validationResult.extend(self.checkStringTypeRestrictions(jsonObject))
        elif jsonObject.propType == 'array':
            validationResult.extend(self.checkArrayTypeRestrictions(jsonObject))

        return validationResult

    def checkArrayTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (jsonObject.extraInfo
                and 'items' in jsonObject.extraInfo
                and jsonObject.extraInfo['items']
                and isinstance(jsonObject.extraInfo['items'], dict)):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_ARRAY_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)
        #elif (jsonObject.extraInfo):


        return validationResult

    def checkStringTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

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

    def checkDraftVersion(self, draftVersion):
        if draftVersion in JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS:

            draftVersion = JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS_SHORT[
                JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS.index(draftVersion)]

            validatorMsg = OutputMessage(None, MessageType.INFO_TYPE,
                                         JsonObjectValidator.CORRECT_DRAFT_MESSAGE + draftVersion)
        else:
            validatorMsg = OutputMessage(None, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.INCORRECT_DRAFT_MESSAGE + draftVersion)

        return validatorMsg
