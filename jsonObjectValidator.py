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

        if not (hasattr(jsonObject, 'description') and jsonObject.description):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if hasattr(jsonObject, 'type'):
            if jsonObject.type == 'string':
                validationResult.extend(self.checkStringTypeRestrictions(jsonObject))
            elif jsonObject.type == 'array':
                validationResult.extend(self.checkArrayTypeRestrictions(jsonObject))

        return validationResult

    def checkArrayTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (hasattr(jsonObject, 'items')
                and jsonObject.items
                and isinstance(jsonObject.items, dict)):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_ARRAY_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)
        # elif (jsonObject.extraInfo):

        return validationResult

    def checkStringTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not hasattr(jsonObject, 'maxLength'):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_MAX_LENGTH_MESSAGE)
            validationResult.append(validatorMsg)
        elif self.allowedStringMaxLength and jsonObject.maxLength > self.allowedStringMaxLength:
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
