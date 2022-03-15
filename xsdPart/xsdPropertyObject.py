from xsdPart.xsdUtils import getStringWithoutNamespace


class XsdPropertyObject(object):
    def __init__(self, xsdTag, parentPath, otherXsdObjects):

        if hasattr(xsdTag, 'prefix') and xsdTag.prefix:
            self.tag = xsdTag.tag.split('}')[1]
        else:
            self.tag = xsdTag.tag

        for attribKey in xsdTag.attrib:
            if attribKey == 'type':
                self.type = getStringWithoutNamespace(
                    xsdTag.attrib['type'])
            else:
                self.__dict__[attribKey] = getStringWithoutNamespace(
                    xsdTag.attrib[attribKey])

        # if 'name' in xsdTag.attrib:
        #     self.name = xsdTag.attrib['name']
        # if 'type' in xsdTag.attrib:
        #     self.type = getStringWithoutNamespaceNamespace(xsdTag.attrib['type'])

        if not hasattr(self, 'type'):
            if hasattr(self, 'base'):
                self.type = self.base
            else:
                self.type = ''

        if next((True for innerTagName in xsdTag.__dict__ if
                 innerTagName in ['complexType', 'group', 'all', 'choice',
                                  'sequence']),
                False):
            self.type = 'object'
            # innerTagName in ['group', 'all', 'choice', 'sequence']),

        if not self.type:
            if baseType := self.getBaseType(xsdTag):
                self.type = baseType

        for propKey, propTag in xsdTag.__dict__.items():

            # if str(xsdTag.__dict__[propKey]):
            #     print("yes")
            # else:
            #     print("nope")

            if propKey not in ['complexType', 'group', 'all', 'choice',
                               'sequence']:
                if propKey == 'annotation' and 'documentation' in \
                        propTag.__dict__.keys():
                    self.__dict__[propKey] = propTag.__dict__[
                        'documentation'].text
                elif propKey == 'simpleType':
                    if hasattr(propTag, 'restriction'):
                        self.parseRestrictions(propTag, 'restriction')

                    if hasattr(propTag, 'list') \
                            and hasattr(propTag.list, 'attrib') \
                            and 'itemType' in propTag.list.attrib:
                        self.type = getStringWithoutNamespace(
                            propTag.list.attrib['itemType'])

                elif propKey == 'restriction' or propKey == 'extension':
                    self.parseRestrictions(xsdTag, propKey)
                elif propKey == 'enumeration':
                    if hasattr(self, 'enumeration'):
                        self.enumeration += propTag
                    else:
                        self.enumeration = propTag

                else:
                    self.__dict__[propKey] = propTag
            # elif not hasattr(self, 'type'):
            #    self.type = 'object'

        if not hasattr(self, 'name'):
            if hasattr(self, 'ref'):
                self.name = getStringWithoutNamespace(self.ref)
            elif hasattr(self, 'base'):
                self.name = getStringWithoutNamespace(self.base)
            else:
                self.name = 'elem№' + str(otherXsdObjects.__len__() + 1)

        self.fullPath = parentPath + '/' + self.name

        if f'/{self.name}/' in self.fullPath:
            self.isCycle = True

        self.reset()

    def getBaseType(self, parentTag):
        for childTag in parentTag.iterchildren():
            if hasattr(childTag, 'attrib') and 'base' in childTag.attrib:
                return getStringWithoutNamespace(
                    childTag.attrib['base'])
            else:
                if baseType := self.getBaseType(childTag):
                    return baseType

        return

    def parseRestrictions(self, xsdTag, propKey):
        restrictionsMainTag = xsdTag.__dict__[propKey]
        if 'base' in restrictionsMainTag.attrib:
            self.type = getStringWithoutNamespace(
                restrictionsMainTag.attrib['base'])

        # if 'pattern' in xsdTag.__dict__[propKey].__dict__.keys():
        for restrictionName in restrictionsMainTag.__dict__.keys():
            restrictionTag = restrictionsMainTag.__dict__[restrictionName]
            if hasattr(restrictionTag,
                       'tag') and not restrictionTag.tag.endswith('attribute'):
                for i in range(len(restrictionTag)):
                    if hasattr(restrictionTag[i], 'attrib'):
                        for attrib in restrictionTag[i].attrib:
                            if restrictionName in self.__dict__:
                                self.__dict__[
                                    restrictionName] += f', {restrictionTag[i].attrib[attrib]}'
                            else:
                                self.__dict__[restrictionName] = \
                                    restrictionTag[i].attrib[attrib]

    def reset(self):
        self.tabsCount = 1

    def __str__(self) -> str:
        PROPERTY_STRING = '\n' + ('\t' * self.tabsCount) + '%s: %s;'

        returnString = ('\t' * (self.tabsCount - 1)) + '{'

        for fieldName in self.__dict__:
            if fieldName != 'tabsCount':
                fieldValue = self.__dict__[fieldName]
                if isinstance(fieldValue, XsdPropertyObject):
                    fieldValue.tabsCount = self.tabsCount + 1
                    returnString += (PROPERTY_STRING % (
                        fieldName, '\n' + str(fieldValue)))
                else:
                    returnString += (PROPERTY_STRING % (
                        fieldName, str(fieldValue) + ''))

        returnString += '\n' + ('\t' * (self.tabsCount - 1)) + '}'

        self.reset()
        return returnString
