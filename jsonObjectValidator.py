from outputMessage import MessageType
from outputMessage import OutputMessage
import re


class JsonObjectValidator(object):
    NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание (аннотация) элемента'
    NO_TYPE_MESSAGE = 'Не указан тип элемента'
    POSSIBLE_KEY_VALUE_MESSAGE = 'Возможная структура key-value'
    COMPLEX_TYPE_ADDITIONAL_PROPERTIES_MESSAGE = 'Для элементов комплексного типа ' \
                                                 'должно быть указано "additionalProperties": false'

    STRING_NO_MAX_LENGTH_MESSAGE = 'Отсутствует ограничение по длине строки'
    STRING_NO_PATTERN_MESSAGE = 'Отсутствует паттерн для строки'
    STRING_EXCESS_MAX_LENGTH_MESSAGE = 'Указаная максимальная длина строки выше допустимой'

    ARRAY_NO_ITEMS_MESSAGE = 'Для массива не определен блок items'
    ARRAY_NO_MAX_ITEMS_MESSAGE = 'Для массива не указано максимальное количество элементов'
    ARRAY_EXCESS_MAX_ITEMS_MESSAGE = 'Указанное максимальное количество элементов превышает допустимое'
    ARRAY_ADDITIONAL_ITEMS_MESSAGE = 'Для массива не указано "additionalItems": false'
    ARRAY_UNIQUE_ITEMS_MESSAGE = 'Для массива не указано "uniqueItems": true'

    NUMERIC_NO_MIN_VALUE_MESSAGE = 'Не указано минимальное значение для числа'
    NUMERIC_NO_MAX_VALUE_MESSAGE = 'Не указано максимальное значение для числа'
    NUMERIC_EXCESS_MAX_VALUE_MESSAGE = 'Указанное максимальное значение для числа превышает допустимое'
    NUMERIC_EXCESS_MIN_VALUE_MESSAGE = 'Указанное минимальное значение для числа меньше допустимого'

    DRAFT_4_SHORT_DEFINITION = 'draft-04'
    DRAFT_7_SHORT_DEFINITION = 'draft-07'
    AVAILABLE_DRAFT_VERSIONS_SHORT = [DRAFT_4_SHORT_DEFINITION, DRAFT_7_SHORT_DEFINITION]
    AVAILABLE_DRAFT_VERSIONS = [f'http://json-schema.org/{x}/schema#' for x in AVAILABLE_DRAFT_VERSIONS_SHORT]
    CORRECT_DRAFT_MESSAGE = 'В схеме использована версия драфта: '
    INCORRECT_DRAFT_MESSAGE = 'В схеме использована некорректная версия драфта: '

    def __init__(self, configWidget):
        self.configElements = {elem.objectName(): elem for elem in configWidget.children()}

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

        if self.configElements.get('confCheckTypeLabel').isChecked() and not hasattr(jsonObject, 'type'):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_TYPE_MESSAGE)
            validationResult.append(validatorMsg)

        if self.isComplexType(jsonObject):
            if not (hasattr(jsonObject, 'additionalProperties') and not jsonObject.additionalProperties):
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.COMPLEX_TYPE_ADDITIONAL_PROPERTIES_MESSAGE)
                validationResult.append(validatorMsg)

        if hasattr(jsonObject, 'name') and re.search('key|param|value', jsonObject.name, re.IGNORECASE):
            validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
                                         JsonObjectValidator.POSSIBLE_KEY_VALUE_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult

    def checkNumericTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if self.configElements.get('confNumericMinLabel').isChecked():
            if not hasattr(jsonObject, 'minimum'):
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.NUMERIC_NO_MIN_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get('confNumericMinText').toPlainText().isdigit():
                expectedMinNumber = int(self.configElements.get('confNumericMinText').toPlainText())
                actualMinNumber = jsonObject.minimum + 1 \
                    if hasattr(jsonObject, 'exclusiveMinimum') and jsonObject.exclusiveMinimum else jsonObject.minimum

                if expectedMinNumber > actualMinNumber:
                    validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                                 JsonObjectValidator.NUMERIC_EXCESS_MIN_VALUE_MESSAGE)
                    validationResult.append(validatorMsg)

        if self.configElements.get('confNumericMaxLabel').isChecked():
            if not hasattr(jsonObject, 'maximum'):
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.NUMERIC_NO_MAX_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get('confNumericMaxText').toPlainText().isdigit():
                expectedMaxNumber = int(self.configElements.get('confNumericMaxText').toPlainText())
                actualMaxNumber = jsonObject.minimum - 1 \
                    if hasattr(jsonObject, 'exclusiveMaximum') and jsonObject.exclusiveMaximum else jsonObject.maximum

                if expectedMaxNumber < actualMaxNumber:
                    validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                                 JsonObjectValidator.NUMERIC_EXCESS_MAX_VALUE_MESSAGE)
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

        if self.configElements.get('confArrayLengthLabel').isChecked():
            if not (hasattr(jsonObject, 'maxItems') and jsonObject.maxItems):
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.ARRAY_NO_MAX_ITEMS_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get('confArrayLengthText').toPlainText().isdigit() \
                    and int(self.configElements.get('confArrayLengthText').toPlainText()) < jsonObject.maxItems:
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.ARRAY_EXCESS_MAX_ITEMS_MESSAGE)
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

        if self.configElements.get('confStringLengthLabel').isChecked():
            if not hasattr(jsonObject, 'maxLength'):

                if not hasattr(jsonObject, 'pattern') \
                        or re.search('([^\\[]+\\+[^]]+)|\\*', jsonObject.pattern):
                    validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                                 JsonObjectValidator.STRING_NO_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)

            elif self.configElements.get('confStringLengthText').toPlainText().isdigit() \
                    and int(self.configElements.get('confStringLengthText').toPlainText()) < jsonObject.maxLength:
                validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                             JsonObjectValidator.STRING_EXCESS_MAX_LENGTH_MESSAGE)
                validationResult.append(validatorMsg)

        # if not hasattr(jsonObject, 'pattern'):
        #     validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
        #                                  JsonObjectValidator.STRING_NO_PATTERN_MESSAGE)
        #     validationResult.append(validatorMsg)

        return validationResult

    def checkStringPattern(self, jsonObject) -> list:
        validationResult = []

        if hasattr(jsonObject, 'type') \
                and jsonObject.type == 'string' \
                and not hasattr(jsonObject, 'pattern'):
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
