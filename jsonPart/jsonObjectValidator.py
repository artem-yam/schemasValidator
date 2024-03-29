import re

import baseUtils
import jsonPart.jsonUtils as jsonUtils
from outputMessage import MessageType
from outputMessage import OutputMessage


class JsonObjectValidator(object):
    NO_TYPE_MESSAGE = 'Не указан тип элемента'
    NO_ADDITIONAL_PROPERTIES_MESSAGE = 'Для элементов с типом "object" ' \
                                       'должно быть указано ' \
                                       '"additionalProperties":false'
    NO_MAX_PROPERTIES_MESSAGE = 'При наличии "patternProperties" должно быть ' \
                                'указано "maxProperties"'
    ARRAY_NO_ITEMS_MESSAGE = 'Для массива не определен блок items'
    ARRAY_NO_MAX_ITEMS_MESSAGE = 'Для массива не указано максимальное ' \
                                 'количество элементов'
    ARRAY_ADDITIONAL_ITEMS_MESSAGE = 'Для массива не указано ' \
                                     '"additionalItems": false'
    ARRAY_UNIQUE_ITEMS_MESSAGE = 'Для массива не указано "uniqueItems": true'

    DRAFT_4_SHORT_DEFINITION = 'draft-04'
    DRAFT_7_SHORT_DEFINITION = 'draft-07'
    AVAILABLE_DRAFT_VERSIONS_SHORT = [DRAFT_4_SHORT_DEFINITION,
                                      DRAFT_7_SHORT_DEFINITION]
    AVAILABLE_DRAFT_VERSIONS = [f'http://json-schema.org/{x}/schema#' for x in
                                AVAILABLE_DRAFT_VERSIONS_SHORT]
    CORRECT_DRAFT_MESSAGE = 'В схеме использована версия драфта: '
    INCORRECT_DRAFT_MESSAGE = \
        'В схеме использована некорректная версия драфта: '

    def __init__(self, configWidget):
        self.configElements = {elem.objectName(): elem for elem in
                               configWidget.children()}

    def validate(self, jsonObject, objectsDict):
        validationResult = self.checkBaseRestrictions(jsonObject, objectsDict)

        if hasattr(jsonObject, 'type'):
            if jsonObject.type == 'string':
                validationResult.extend(
                    self.checkStringTypeRestrictions(jsonObject))
            elif jsonObject.type == 'array':
                validationResult.extend(
                    self.checkArrayTypeRestrictions(jsonObject))
            elif jsonObject.type == 'number' or jsonObject.type == 'integer':
                validationResult.extend(
                    self.checkNumericTypeRestrictions(jsonObject))

        return validationResult

    # def checkCardNumber(self, objectsDict) -> list:
    #     validationResult = []
    #
    #     for jsonObject in objectsDict.values():
    #         if hasattr(jsonObject, 'name') and re.search(
    #                 'card|cardnum|number|cardnumber',
    #                 jsonObject.name, re.IGNORECASE):
    #             validatorMsg = OutputMessage(jsonObject, MessageType.INFO_TYPE,
    #                                          JsonObjectValidator.POSSIBLE_CARD_NUMBER_MESSAGE)
    #             validationResult.append(validatorMsg)
    #
    #     return validationResult

    def checkBaseRestrictions(self, jsonObject, objectsDict) -> list:
        validationResult = []

        if hasattr(jsonObject, 'name') and re.search(
                'card|cardnum|number|cardnumber',
                jsonObject.name, re.IGNORECASE):
            validatorMsg = OutputMessage(
                jsonObject, MessageType.INFO_TYPE,
                baseUtils.POSSIBLE_CARD_NUMBER_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(jsonObject, 'description') and jsonObject.description):
            validatorMsg = OutputMessage(
                jsonObject, MessageType.INFO_TYPE,
                baseUtils.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if self.configElements.get('jsonConfCheckTypeLabel').isChecked() \
                and not hasattr(jsonObject, 'type') \
                and not (hasattr(jsonObject, '$ref')
                         and isinstance(objectsDict, dict)
                         and any(hasattr(x, 'fullPath')
                                 and x.fullPath == jsonObject.__dict__['$ref']
                                 for x in
                                 objectsDict.values())):
            validatorMsg = OutputMessage(jsonObject, MessageType.ERROR_TYPE,
                                         JsonObjectValidator.NO_TYPE_MESSAGE)
            validationResult.append(validatorMsg)

        if jsonUtils.isComplexType(jsonObject):
            if not hasattr(jsonObject, 'additionalProperties') \
                    or jsonObject.additionalProperties is True:
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    JsonObjectValidator.NO_ADDITIONAL_PROPERTIES_MESSAGE)
                validationResult.append(validatorMsg)
            elif jsonObject.additionalProperties:
                if not (hasattr(jsonObject, 'maxProperties')
                        and jsonObject.maxProperties):
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        JsonObjectValidator.NO_MAX_PROPERTIES_MESSAGE)
                    validationResult.append(validatorMsg)

            if hasattr(jsonObject, 'patternProperties'):
                if not (hasattr(jsonObject, 'maxProperties')
                        and jsonObject.maxProperties):
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        JsonObjectValidator.NO_MAX_PROPERTIES_MESSAGE)
                    validationResult.append(validatorMsg)

        if hasattr(jsonObject, 'name') and (
                (isKey := re.search('key|param', jsonObject.name,
                                    re.IGNORECASE))
                or (isValue := re.search('value', jsonObject.name,
                                         re.IGNORECASE))):
            isPossibleKeyValue = False

            for siblingObjectKey, siblingObject \
                    in baseUtils.getElementSiblings(jsonObject,
                                                    objectsDict).items():
                if hasattr(siblingObject, 'name'):
                    if isKey is not None:
                        isPossibleKeyValue = re.search('value',
                                                       siblingObject.name,
                                                       re.IGNORECASE)
                    else:
                        isPossibleKeyValue = re.search('key|param',
                                                       siblingObject.name,
                                                       re.IGNORECASE)
                    if isPossibleKeyValue:
                        break

            if isPossibleKeyValue:
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.INFO_TYPE,
                    baseUtils.POSSIBLE_KEY_VALUE_MESSAGE)
                validationResult.append(validatorMsg)

        return validationResult

    def checkNumericTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if self.configElements.get('jsonConfNumericMinLabel').isChecked():
            if not hasattr(jsonObject, 'minimum'):
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    baseUtils.NUMERIC_NO_MIN_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get(
                    'jsonConfNumericMinText').toPlainText().isdigit():
                expectedMinNumber = int(
                    self.configElements.get(
                        'jsonConfNumericMinText').toPlainText())
                actualMinNumber = jsonObject.minimum + 1 \
                    if (hasattr(jsonObject, 'exclusiveMinimum')
                        and jsonObject.exclusiveMinimum) else jsonObject.minimum

                if expectedMinNumber > actualMinNumber:
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        baseUtils.NUMERIC_EXCESS_MIN_VALUE_MESSAGE)
                    validationResult.append(validatorMsg)

        if self.configElements.get('jsonConfNumericMaxLabel').isChecked():
            if not hasattr(jsonObject, 'maximum'):
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    baseUtils.NUMERIC_NO_MAX_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get(
                    'jsonConfNumericMaxText').toPlainText().isdigit():
                expectedMaxNumber = int(
                    self.configElements.get(
                        'jsonConfNumericMaxText').toPlainText())
                actualMaxNumber = jsonObject.minimum - 1 \
                    if (hasattr(jsonObject, 'exclusiveMaximum')
                        and jsonObject.exclusiveMaximum) else jsonObject.maximum

                if expectedMaxNumber < actualMaxNumber:
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        baseUtils.NUMERIC_EXCESS_MAX_VALUE_MESSAGE)
                    validationResult.append(validatorMsg)

        return validationResult

    def checkArrayTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if not (hasattr(jsonObject, 'items')
                and jsonObject.items
                and isinstance(jsonObject.items, str)):
            validatorMsg = OutputMessage(
                jsonObject, MessageType.ERROR_TYPE,
                JsonObjectValidator.ARRAY_NO_ITEMS_MESSAGE)
            validationResult.append(validatorMsg)

        else:

            if self.configElements.get('jsonConfArrayLengthLabel').isChecked():
                if not (hasattr(jsonObject,
                                'maxItems') and jsonObject.maxItems):
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        JsonObjectValidator.ARRAY_NO_MAX_ITEMS_MESSAGE)
                    validationResult.append(validatorMsg)
                elif self.configElements.get(
                        'jsonConfArrayLengthText').toPlainText().isdigit() \
                        and int(self.configElements.get(
                    'jsonConfArrayLengthText').toPlainText()) < jsonObject.maxItems:
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        baseUtils.ARRAY_EXCESS_MAX_ITEMS_MESSAGE)
                    validationResult.append(validatorMsg)

            if not (hasattr(jsonObject, 'additionalItems')
                    and not jsonObject.additionalItems):
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    JsonObjectValidator.ARRAY_ADDITIONAL_ITEMS_MESSAGE)
                validationResult.append(validatorMsg)

            if not (hasattr(jsonObject,
                            'uniqueItems') and jsonObject.uniqueItems):
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    JsonObjectValidator.ARRAY_UNIQUE_ITEMS_MESSAGE)
                validationResult.append(validatorMsg)

        return validationResult

    def checkStringTypeRestrictions(self, jsonObject) -> list:
        validationResult = []

        if self.configElements.get('jsonConfStringLengthLabel').isChecked():
            if not hasattr(jsonObject, 'maxLength'):

                if (not hasattr(jsonObject, 'pattern')
                    or re.search('([^\\[]+\\+)|\\*', jsonObject.pattern)) \
                        and not hasattr(jsonObject, 'enum'):
                    validatorMsg = OutputMessage(
                        jsonObject, MessageType.ERROR_TYPE,
                        baseUtils.STRING_NO_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)

            elif self.configElements.get(
                    'jsonConfStringLengthText').toPlainText().isdigit() \
                    and int(self.configElements.get(
                'jsonConfStringLengthText').toPlainText()) < jsonObject.maxLength:
                validatorMsg = OutputMessage(
                    jsonObject, MessageType.ERROR_TYPE,
                    baseUtils.STRING_EXCESS_MAX_LENGTH_MESSAGE)
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
                and not hasattr(jsonObject, 'pattern') \
                and not hasattr(jsonObject, 'format') \
                and not hasattr(jsonObject, 'enum'):
            validatorMsg = OutputMessage(
                jsonObject, MessageType.INFO_TYPE,
                baseUtils.STRING_NO_PATTERN_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult

    def checkDraftVersion(self, draftVersion):
        if draftVersion in JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS:

            draftVersion = JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS_SHORT[
                JsonObjectValidator.AVAILABLE_DRAFT_VERSIONS.index(
                    draftVersion)]

            validatorMsg = OutputMessage(
                None, MessageType.INFO_TYPE,
                JsonObjectValidator.CORRECT_DRAFT_MESSAGE + draftVersion)
        else:
            validatorMsg = OutputMessage(
                None, MessageType.ERROR_TYPE,
                JsonObjectValidator.INCORRECT_DRAFT_MESSAGE + draftVersion)

        return validatorMsg

