import re

import baseUtils
from outputMessage import MessageType
from outputMessage import OutputMessage


class XsdObjectValidator(object):
    NULL_TYPE_MESSAGE = 'Отсутствует описание типа элемента'
    ANY_TYPE_MESSAGE = 'Присутствует элемент типа \'any\''
    ARRAY_NO_MAX_ITEMS_MESSAGE = 'Для массива не указано максимальное ' \
                                 'количество элементов'
    NUMERIC_WRONG_TOTAL_DIGITS_MESSAGE = 'Не корректно указано totalDigits ' \
                                         'при наличии ограничения ' \
                                         'минимального/максимального значения'
    NUMERIC_EXCESS_TOTAL_DIGITS_MIN_VALUE_MESSAGE \
        = 'Количество цифр для числа не соответствует минимальному ' \
          'допустимому значению'
    NUMERIC_EXCESS_TOTAL_DIGITS_MAX_VALUE_MESSAGE = 'Количество цифр для ' \
                                                    'числа не соответствует ' \
                                                    'максимальному ' \
                                                    'допустимому значению'

    def __init__(self, configWidget):
        self.configElements = {elem.objectName(): elem for elem in
                               configWidget.children()}

    def validate(self, xsdObject, objectsDict):
        validationResult = self.checkBaseRestrictions(xsdObject, objectsDict)

        if hasattr(xsdObject, 'type'):
            if xsdObject.type == 'string':
                validationResult.extend(
                    self.checkStringTypeRestrictions(xsdObject))
            elif xsdObject.type in ['decimal', 'integer',
                                    'negativeInteger', 'nonNegativeInteger',
                                    'nonPositiveInteger', 'positiveInteger']:
                validationResult.extend(
                    self.checkNumericTypeRestrictions(xsdObject))

        if hasattr(xsdObject, 'maxOccurs'):
            validationResult.extend(self.checkArrayRestrictions(xsdObject))

        return validationResult

    # def checkCardNumber(self, objectsDict) -> list:
    #     validationResult = []
    #
    #     for xsdObject in objectsDict.values():
    #         if hasattr(xsdObject, 'name') and re.search(
    #                 'card|cardnum|number|cardnumber',
    #                 xsdObject.name, re.IGNORECASE):
    #             validatorMsg = OutputMessage(xsdObject, MessageType.INFO_TYPE,
    #                                          XsdObjectValidator.POSSIBLE_CARD_NUMBER_MESSAGE)
    #             validationResult.append(validatorMsg)
    #
    #     return validationResult

    def checkBaseRestrictions(self, xsdObject, objectsDict) -> list:
        validationResult = []

        if hasattr(xsdObject, 'name') and re.search(
                'card|cardnum|number|cardnumber',
                xsdObject.name, re.IGNORECASE):
            validatorMsg = OutputMessage(xsdObject, MessageType.INFO_TYPE,
                                         baseUtils.POSSIBLE_CARD_NUMBER_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(xsdObject, 'annotation') and xsdObject.annotation):
            validatorMsg = OutputMessage(xsdObject, MessageType.INFO_TYPE,
                                         baseUtils.NULL_DESCRIPTION_MESSAGE)
            validationResult.append(validatorMsg)

        if not (hasattr(xsdObject, 'type') and xsdObject.type):
            validatorMsg = OutputMessage(xsdObject, MessageType.ERROR_TYPE,
                                         XsdObjectValidator.NULL_TYPE_MESSAGE)
            validationResult.append(validatorMsg)

        if self.configElements.get('xsdConfAnyCheckLabel').isChecked() \
                and hasattr(xsdObject,
                            'type') and xsdObject.type.lower() == 'anytype':
            validatorMsg = OutputMessage(xsdObject, MessageType.ERROR_TYPE,
                                         XsdObjectValidator.ANY_TYPE_MESSAGE)
            validationResult.append(validatorMsg)

        if xsdObject.tag != 'attribute' \
                and hasattr(xsdObject, 'name') \
                and ((isKey := re.search('key|param', xsdObject.name,
                                         re.IGNORECASE))
                     or (isValue := re.search('value', xsdObject.name,
                                              re.IGNORECASE))):
            isPossibleKeyValue = False

            for siblingObjectKey, siblingObject \
                    in baseUtils.getElementSiblings(xsdObject,
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
                    xsdObject,
                    MessageType.INFO_TYPE,
                    baseUtils.POSSIBLE_KEY_VALUE_MESSAGE
                )
                validationResult.append(validatorMsg)

        return validationResult

    def checkNumericTypeRestrictions(self, xsdObject) -> list:
        validationResult = []

        if self.configElements.get('xsdConfNumericMinLabel').isChecked():
            if not ((hasattr(xsdObject, 'minExclusive') and
                     xsdObject.minExclusive.lstrip('-').isdigit())
                    or (hasattr(xsdObject, 'minInclusive') and
                        xsdObject.minInclusive.lstrip('-').isdigit())
                    or (hasattr(xsdObject, 'totalDigits') and
                        xsdObject.totalDigits.lstrip('-').isdigit())):
                validatorMsg = OutputMessage(
                    xsdObject, MessageType.ERROR_TYPE,
                    baseUtils.NUMERIC_NO_MIN_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get('xsdConfNumericMinText') \
                    .toPlainText().lstrip('-').isdigit():
                validatorMsg = None
                expectedMinNumber = int(
                    self.configElements.get(
                        'xsdConfNumericMinText').toPlainText())

                minValues = []
                if hasattr(xsdObject, 'minExclusive'):
                    minValues.append(int(xsdObject.minExclusive))
                if hasattr(xsdObject, 'minInclusive'):
                    minValues.append(int(xsdObject.minInclusive))

                actualMinNumber = max(minValues) if minValues else False
                actualMinNumberTotalDigits = len(
                    str(actualMinNumber)) if actualMinNumber else 0

                expectedMinNumberTotalDigits = len(str(expectedMinNumber))

                if hasattr(xsdObject,
                           'totalDigits') and xsdObject.totalDigits.isdigit():
                    if actualMinNumberTotalDigits > int(xsdObject.totalDigits):
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            XsdObjectValidator.NUMERIC_WRONG_TOTAL_DIGITS_MESSAGE)
                        validationResult.append(validatorMsg)
                    else:
                        actualMinNumberTotalDigits = int(xsdObject.totalDigits)

                if validatorMsg is not None:
                    if minValues and actualMinNumber and expectedMinNumber > \
                            actualMinNumber:
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            baseUtils.NUMERIC_EXCESS_MIN_VALUE_MESSAGE)
                        validationResult.append(validatorMsg)

                    elif (
                            expectedMinNumberTotalDigits <
                            actualMinNumberTotalDigits
                            and expectedMinNumber < 0) or \
                            (
                                    expectedMinNumberTotalDigits >
                                    actualMinNumberTotalDigits
                                    and expectedMinNumber >= 0):
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            XsdObjectValidator.NUMERIC_EXCESS_TOTAL_DIGITS_MIN_VALUE_MESSAGE)
                        validationResult.append(validatorMsg)

        if self.configElements.get('xsdConfNumericMaxLabel').isChecked():
            if not ((hasattr(xsdObject, 'maxExclusive') and
                     xsdObject.maxExclusive.lstrip('-').isdigit())
                    or (hasattr(xsdObject, 'maxInclusive') and
                        xsdObject.maxInclusive.lstrip('-').isdigit())
                    or (hasattr(xsdObject, 'totalDigits') and
                        xsdObject.totalDigits.lstrip('-').isdigit())):
                validatorMsg = OutputMessage(
                    xsdObject, MessageType.ERROR_TYPE,
                    baseUtils.NUMERIC_NO_MAX_VALUE_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get(
                    'xsdConfNumericMaxText').toPlainText().lstrip(
                '-').isdigit():
                validatorMsg = None
                expectedMaxNumber = int(
                    self.configElements.get(
                        'xsdConfNumericMaxText').toPlainText())

                maxValues = []
                if hasattr(xsdObject, 'maxExclusive'):
                    maxValues.append(int(xsdObject.maxExclusive))
                if hasattr(xsdObject, 'maxInclusive'):
                    maxValues.append(int(xsdObject.maxInclusive))

                actualMaxNumber = min(maxValues) if maxValues else False
                actualMaxNumberTotalDigits = len(
                    str(actualMaxNumber)) if actualMaxNumber else 0

                expectedMaxNumberTotalDigits = len(str(expectedMaxNumber))

                if hasattr(xsdObject,
                           'totalDigits') and xsdObject.totalDigits.isdigit():
                    if actualMaxNumberTotalDigits < int(xsdObject.totalDigits):
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            XsdObjectValidator.NUMERIC_WRONG_TOTAL_DIGITS_MESSAGE)
                        validationResult.append(validatorMsg)
                    else:
                        actualMaxNumberTotalDigits = int(xsdObject.totalDigits)

                if validatorMsg is not None:
                    if maxValues and actualMaxNumber and expectedMaxNumber < \
                            actualMaxNumber:
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            baseUtils.NUMERIC_EXCESS_MAX_VALUE_MESSAGE)
                        validationResult.append(validatorMsg)

                    elif (
                            expectedMaxNumberTotalDigits >
                            actualMaxNumberTotalDigits
                            and expectedMaxNumber < 0) or \
                            (
                                    expectedMaxNumberTotalDigits <
                                    actualMaxNumberTotalDigits
                                    and expectedMaxNumber >= 0):
                        validatorMsg = OutputMessage(
                            xsdObject, MessageType.ERROR_TYPE,
                            XsdObjectValidator.NUMERIC_EXCESS_TOTAL_DIGITS_MAX_VALUE_MESSAGE)
                        validationResult.append(validatorMsg)

        return validationResult

    def checkArrayRestrictions(self, xsdObject) -> list:
        validationResult = []

        if self.configElements.get('xsdConfArrayLengthLabel').isChecked():
            if xsdObject.maxOccurs == 'unbounded':
                validatorMsg = OutputMessage(
                    xsdObject, MessageType.ERROR_TYPE,
                    XsdObjectValidator.ARRAY_NO_MAX_ITEMS_MESSAGE)
                validationResult.append(validatorMsg)
            elif self.configElements.get(
                    'xsdConfArrayLengthText').toPlainText().isdigit() \
                    and xsdObject.maxOccurs.isdigit() \
                    and int(self.configElements.get(
                'xsdConfArrayLengthText').toPlainText()) < int(
                xsdObject.maxOccurs):
                validatorMsg = OutputMessage(
                    xsdObject, MessageType.ERROR_TYPE,
                    baseUtils.ARRAY_EXCESS_MAX_ITEMS_MESSAGE)
                validationResult.append(validatorMsg)

        return validationResult

    def checkStringTypeRestrictions(self, xsdObject) -> list:
        validationResult = []

        if self.configElements.get('xsdConfStringLengthLabel').isChecked():
            if not (hasattr(xsdObject,
                            'maxLength') and xsdObject.maxLength.isdigit()
                    or hasattr(xsdObject,
                               'length') and xsdObject.length.isdigit()):

                if (not hasattr(xsdObject, 'pattern')
                    or re.search('([^\\[]+\\+)|\\*', xsdObject.pattern)) \
                        and not hasattr(xsdObject, 'enumeration'):
                    validatorMsg = OutputMessage(
                        xsdObject, MessageType.ERROR_TYPE,
                        baseUtils.STRING_NO_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)

            elif self.configElements.get(
                    'xsdConfStringLengthText').toPlainText().isdigit():
                maxAllowedLength = int(
                    self.configElements.get(
                        'xsdConfStringLengthText').toPlainText())

                if (hasattr(xsdObject, 'maxLength') and
                    maxAllowedLength < int(xsdObject.maxLength)) or \
                        (hasattr(xsdObject,
                                 'length') and maxAllowedLength < int(
                            xsdObject.length)):
                    validatorMsg = OutputMessage(
                        xsdObject, MessageType.ERROR_TYPE,
                        baseUtils.STRING_EXCESS_MAX_LENGTH_MESSAGE)
                    validationResult.append(validatorMsg)

        return validationResult

    def checkStringPattern(self, xsdObject) -> list:
        validationResult = []

        # TODO фикс проверок + учитывать расширения базовой строки
        if hasattr(xsdObject, 'type') \
                and xsdObject.type == 'string' \
                and not hasattr(xsdObject, 'pattern') \
                and not hasattr(xsdObject, 'enumeration'):
            validatorMsg = OutputMessage(
                xsdObject, MessageType.INFO_TYPE,
                baseUtils.STRING_NO_PATTERN_MESSAGE)
            validationResult.append(validatorMsg)

        return validationResult
