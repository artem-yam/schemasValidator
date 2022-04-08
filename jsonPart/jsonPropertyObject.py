class JsonPropertyObject(object):
    def __init__(self, jsonMap):
        self.tabsCount = None
        if isinstance(jsonMap, dict):
            self.__dict__.update(jsonMap)

        self.reset()

    def reset(self):
        self.tabsCount = 1

    def __str__(self) -> str:
        PROPERTY_STRING = '\n' + ('\t' * self.tabsCount) + '%s: %s;'
        # PROPERTY_STRING = '\n' + ('\t' * '{}') + '{}: {};'

        returnString = ('\t' * (self.tabsCount - 1)) + '{'

        for fieldName in self.__dict__:
            if fieldName != 'tabsCount':
                fieldValue = self.__dict__[fieldName]
                if isinstance(fieldValue, JsonPropertyObject):
                    fieldValue.tabsCount = self.tabsCount + 1
                    returnString += (PROPERTY_STRING % (
                        fieldName, '\n' + str(fieldValue)))
                else:
                    returnString += (PROPERTY_STRING % (
                        fieldName, str(fieldValue) + ''))

        returnString += '\n' + ('\t' * (self.tabsCount - 1)) + '}'

        self.reset()
        return returnString

    def isEmpty(self) -> bool:
        result = True
        if len(self.__dict__) > 1:
            result = False

        return result
