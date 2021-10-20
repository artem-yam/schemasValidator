from outputMessage import MessageType
from outputMessage import OutputMessage


class JsonObjectValidator(object):
    NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание элемента'
    NO_TYPE_MESSAGE = 'Не указан тип элемента'
    COMPLEX_TYPE_ADDITIONAL_PROPERTIES_MESSAGE = 'Для элементов комплексного типа ' \
                                                 'должно быть указано "additionalProperties": false'

    STRING_NO_MAX_LENGTH_MESSAGE = 'Отсутствует ограничение по длине строки'
    STRING_NO_PATTERN_MESSAGE = 'Отсутствует паттерн для строки'
    STRING_EXCESS_MAX_LENGTH_MESSAGE = 'Указаная максимальная длина строки выше допустимой'

    ARRAY_NO_ITEMS_MESSAGE = 'Для массива не определен блок items'
    ARRAY_NO_MAX_ITEMS_MESSAGE = 'Для массива не указано маскимальное количество элементов'
    ARRAY_ADDITIONAL_ITEMS_MESSAGE = 'Для массива не указано "additionalItems": false'
    ARRAY_UNIQUE_ITEMS_MESSAGE = 'Для массива не указано "uniqueItems": true'

    NUMERIC_NO_MIN_VALUE_MESSAGE = 'Не указано минимальное значение для числа'
    NUMERIC_NO_MAX_VALUE_MESSAGE = 'Не указано максимальное значение для числа'

    DRAFT_4_SHORT_DEFINITION = 'draft-04'
    DRAFT_7_SHORT_DEFINITION = 'draft-07'
    AVAILABLE_DRAFT_VERSIONS_SHORT = [DRAFT_4_SHORT_DEFINITION, DRAFT_7_SHORT_DEFINITION]
    AVAILABLE_DRAFT_VERSIONS = [f'http://json-schema.org/{x}/schema#' for x in AVAILABLE_DRAFT_VERSIONS_SHORT]
    CORRECT_DRAFT_MESSAGE = 'В схеме использована версия драфта: '
    INCORRECT_DRAFT_MESSAGE = 'В схеме использована некорректная версия драфта: '

    def __init__(self, form):
        super().__init__()
        self.allowedStringMaxLength = 0

    def validate(self, jsonObject):
        validationResult = self.checkBaseRestrictions(jsonObject)

        if hasattr(jsonObject, 'type'):
            if jsonObject.type == 'string':
                validationResult.extend(self.checkStringTypeRestrictions(jsonObject))
            elif jsonObject.type == 'array':
                validationResult.extend(self.checkArrayTypeRestrictions(jsonObject))
            elif jsonObject.type == 'number' or jsonObject.type == 'integer':
                validationResult.extend(self.checkNumericTypeRestrictions(jsonObject))

        return validationResult

    def checkBaseRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (hasattr(jsonObject, 'description') and jsonObject.description):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if not hasattr(jsonObject, 'type'):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_TYPE_MESSAGE)
            validationResult.append(validatorMsg)

        if self.isComplexType(jsonObject):
            if not (hasattr(jsonObject, 'additionalProperties') and jsonObject.additionalProperties == 'false'):
                validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                             JsonObjectValidator.COMPLEX_TYPE_ADDITIONAL_PROPERTIES_MESSAGE)
                validationResult.append(validatorMsg)

        return validationResult

    def checkNumericTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (hasattr(jsonObject, 'minimum') or hasattr(jsonObject, 'exclusiveMinimum')):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NUMERIC_NO_MIN_VALUE_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(jsonObject, 'maximum') or hasattr(jsonObject, 'exclusiveMaximum')):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.NUMERIC_NO_MAX_VALUE_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult

    def checkArrayTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (hasattr(jsonObject, 'items')
                and jsonObject.items
                and isinstance(jsonObject.items, str)):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.ARRAY_NO_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(jsonObject, 'maxItems') and jsonObject.maxItems):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.ARRAY_NO_MAX_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(jsonObject, 'additionalItems') and not jsonObject.additionalItems):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.ARRAY_ADDITIONAL_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(jsonObject, 'uniqueItems') and jsonObject.uniqueItems):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.ARRAY_UNIQUE_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult

    def checkStringTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not hasattr(jsonObject, 'maxLength'):
            # TODO поиск ограничения длины по паттерну
            if not hasattr(jsonObject, 'pattern') \
                    or (jsonObject.pattern.__contains__('+') or jsonObject.pattern.__contains__('*')):
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.STRING_NO_MAX_LENGTH_MESSAGE)
                validationResult.append(validatorMsg)

        elif self.allowedStringMaxLength and jsonObject.maxLength > self.allowedStringMaxLength:
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.STRING_EXCESS_MAX_LENGTH_MESSAGE)
            validationResult.append(validatorMsg)

        if not hasattr(jsonObject, 'pattern'):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.STRING_NO_PATTERN_MESSAGE)
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

    def isComplexType(self, jsonObject) -> bool:
        result = False

        if hasattr(jsonObject, 'type'):
            objectType = jsonObject.type

            if not (objectType == 'string' or objectType == 'number' or objectType == 'integer'
                    or objectType == 'boolean' or objectType == 'null'):
                result = True

        return result
