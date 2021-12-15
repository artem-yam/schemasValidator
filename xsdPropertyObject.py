class XsdPropertyObject(object):
    def __init__(self, xsdTag):

        if hasattr(xsdTag, 'prefix') and xsdTag.prefix:
            self.tag = xsdTag.tag.split('}')[1]
        else:
            self.tag = xsdTag.tag

        for attribKey in xsdTag.attrib:
            if attribKey == 'type':
                self.type = self.getStringWithoutNamespaceNamespace(xsdTag.attrib['type'])
            else:
                self.__dict__[attribKey] = xsdTag.attrib[attribKey]

        # if 'name' in xsdTag.attrib:
        #     self.name = xsdTag.attrib['name']
        # if 'type' in xsdTag.attrib:
        #     self.type = self.getStringWithoutNamespaceNamespace(xsdTag.attrib['type'])

        if not hasattr(self, 'type') and (
                (True for innerTagName in xsdTag.__dict__ if
                 innerTagName in ['complexType', 'group', 'all', 'choice', 'sequence']), False):
            self.type = 'object'
            # innerTagName in ['group', 'all', 'choice', 'sequence']),

        for propKey in xsdTag.__dict__:

            # if str(xsdTag.__dict__[propKey]):
            #     print("yes")
            # else:
            #     print("nope")

            if propKey not in ['complexType', 'group', 'all', 'choice', 'sequence']:
                if propKey == 'annotation' and 'documentation' in \
                        xsdTag.__dict__[propKey].__dict__.keys():
                    self.__dict__[propKey] = xsdTag.__dict__[propKey].__dict__['documentation'].text
                elif propKey == 'simpleType':
                    if hasattr(xsdTag.__dict__[propKey], 'restriction'):
                        self.parseRestrictions(xsdTag.__dict__[propKey], 'restriction')
                elif propKey == 'restriction' or propKey == 'extension':
                    self.parseRestrictions(xsdTag, propKey)

                else:
                    self.__dict__[propKey] = xsdTag.__dict__[propKey]
            # elif not hasattr(self, 'type'):
            #    self.type = 'object'

        if not hasattr(self, 'name') and hasattr(self, 'ref'):
            self.name = self.ref

        self.reset()

    def getStringWithoutNamespaceNamespace(self, originalString) -> str:
        namespaceSplit = originalString.split(':')
        return namespaceSplit[len(namespaceSplit) - 1].strip()

    def parseRestrictions(self, xsdTag, propKey):
        restrictionsMainTag = xsdTag.__dict__[propKey]
        if 'base' in restrictionsMainTag.attrib:
            self.type = self.getStringWithoutNamespaceNamespace(restrictionsMainTag.attrib['base'])

        # if 'pattern' in xsdTag.__dict__[propKey].__dict__.keys():
        for restrictionName in restrictionsMainTag.__dict__.keys():
            restrictionTag = restrictionsMainTag.__dict__[restrictionName]
            if hasattr(restrictionTag, 'attrib'):
                for attrib in restrictionTag.attrib:
                    self.__dict__[restrictionName] = restrictionTag.attrib[attrib]

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
                    returnString += (PROPERTY_STRING % (fieldName, '\n' + str(fieldValue)))
                else:
                    returnString += (PROPERTY_STRING % (fieldName, str(fieldValue) + ''))

        returnString += '\n' + ('\t' * (self.tabsCount - 1)) + '}'

        self.reset()
        return returnString
