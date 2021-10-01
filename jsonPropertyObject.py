import copy


class JsonPropertyObject(object):
    def __init__(self, name, fullPath, description, propType, extraInfo):
        self.name = name
        self.fullPath = fullPath
        self.description = description
        self.propType = propType
        self.extraInfo = extraInfo

        self.reset()

    def reset(self):
        self.tabsCount = 1

    def printExtraInfo(self) -> str:
        returnString = ''

        if self.extraInfo is not None:
            returnString += '\n' + ('\t' * self.tabsCount) + 'extraInfo: '

            tempExtraInfo = copy.deepcopy(self.extraInfo)

            # innerProps = ['oneOf'] & tempExtraInfo.keys()
            # if innerProps:
            if 'oneOf' in tempExtraInfo:
                returnString += '\n' + ('\t' * self.tabsCount) + '{\n'

                # returnString += '\n' + ('\t' * self.tabsCount) + '{'
                returnString += ('\t' * (self.tabsCount + 1)) + 'oneOf' + ': '
                propValue = tempExtraInfo['oneOf']
                # print(type(oneOfList))
                for elem in propValue:
                    elem.tabsCount += 2
                    returnString += '\n' + str(elem)
                    # print(elem)

                tempExtraInfo.pop('oneOf')

                returnString += '\n' + ('\t' * self.tabsCount) + '};'

            elif 'items' in tempExtraInfo:
                returnString += '\n' + ('\t' * self.tabsCount) + '{\n'
                returnString += ('\t' * (self.tabsCount + 1)) + 'items:'

                propValue = tempExtraInfo['items']
                propValue.tabsCount += 4
                returnString += '\n' + str(propValue)

                returnString += '\n' + ('\t' * self.tabsCount) + '};'
                tempExtraInfo.pop('items')
            elif 'properties' in tempExtraInfo:
                returnString += '\n' + ('\t' * self.tabsCount) + '{\n'
                returnString += ('\t' * (self.tabsCount + 1)) + 'properties' + ': '
                propValue = tempExtraInfo['properties']
                propValue.tabsCount = self.tabsCount + 1

                if type(propValue.extraInfo) is dict:
                    returnString += '\n' + ('\t' * propValue.tabsCount) + '{'

                    propsDict = propValue.extraInfo

                    for key in propsDict.keys():
                        returnString += '\n' + ('\t' * (propValue.tabsCount + 1)) + key + ':'
                        propsDict[key].tabsCount += propValue.tabsCount + 1
                        returnString += '\n' + str(propsDict[key])
                else:
                    propValue.tabsCount += 2
                    returnString += '\n' + str(propValue)

                # print('propValue.extraInfo: ' + str(propValue.extraInfo))

                returnString += '\n' + ('\t' * propValue.tabsCount) + '};'
                tempExtraInfo.pop('properties')

            if tempExtraInfo.keys() == self.extraInfo.keys():
                returnString += str(tempExtraInfo) + ';' if tempExtraInfo is not None else ''
            else:
                for remainingInfoKey in tempExtraInfo.keys():
                    returnString += '\n' + ('\t' * (self.tabsCount + 1)) + remainingInfoKey + ': ' + str(
                        tempExtraInfo[remainingInfoKey]) + ';'

        return returnString

    def __str__(self) -> str:
        PROPERTY_STRING = '\n' + ('\t' * self.tabsCount) + '%s: %s;'
        # self.NONE_PROPERTY_STRING = '\n' + ('\t' * self.tabsCount) + '%s: None;'

        returnString = ('\t' * (self.tabsCount - 1)) + '{'

        if self.name is not None:
            returnString += (PROPERTY_STRING % ('name', self.name))

        if self.fullPath:
            returnString += (PROPERTY_STRING % ('path', self.fullPath))

        if self.description is not None:
            returnString += (PROPERTY_STRING % ('description', self.description))

        if self.propType is not None:
            returnString += (PROPERTY_STRING % ('type', self.propType))

        returnString += self.printExtraInfo()

        returnString += '\n' + ('\t' * (self.tabsCount - 1)) + '};'

        self.reset()
        return returnString
