import sys
import traceback
from xml.dom.minidom import parseString
from yattag import indent

from lxml import objectify

from xsdPropertyObject import XsdPropertyObject


class XsdParser(object):

    def __init__(self, form):
        super().__init__()
        self.form = form

    def parseFileToText(self, filePath) -> str:
        print("Url = " + filePath)
        xsdString = 'Ошибка загрузки файла'
        try:
            with open(filePath,
                      encoding=sys.getfilesystemencoding()) as xsdFile:
                xml = xsdFile.read()
                xsdFile.close()
        except Exception as err:
            print('Ошибки открытия файла:\n', traceback.format_exc())

        if 'xml' in locals():
            try:
                # from yattag import indent
                # xsdString = indent(xml, indentation=4 * ' ')

                # from xml.dom.minidom import parseString
                xsdString = '\n'.join(
                    [line for line in parseString(xml).toprettyxml(indent=4 * ' ').split('\n') if
                     line.strip()])
            except Exception as err:
                print('Ошибки загрузки файла:\n', traceback.format_exc())

        return xsdString

    def parseTextToObjects(self, xsdString) -> dict:
        xsdObjects = {}
        try:
            # xsdString = xsd.loads(xsdString)
            xsdStringEecode = xsdString.encode()
            rootSchemaTag = objectify.fromstring(xsdString.encode())
            # rootSchemaTag2 = untangle.parse(xsdString)

            xsdObjects.update(self.parseElements(rootSchemaTag, ''))

            print('---------------------------------------------------')
            print(';\n'.join(map(str, xsdObjects.values())))

            if not xsdObjects:
                raise Exception("Объекты в xsd не обнаружены")

        except Exception as err:
            print('Ошибки получения объектов из xsd:\n', traceback.format_exc())
            xsdObjects = 'Ошибка преобразования xsd в объект, проверьте корректность загруженного текста'

        return xsdObjects

    def parseElements(self, schemaTag, parentPath) -> dict:
        xsdObjects = {}

        for tag in schemaTag.iterchildren():
            if hasattr(tag, 'element'):
                xsdObjects.update(self.parseElements(tag.element, parentPath))
            else:
                xsdObject = XsdPropertyObject(tag)

                if hasattr(xsdObject, 'name'):
                    xsdObject.fullPath = parentPath + '/' + xsdObject.name
                    xsdObjects[xsdObject.fullPath] = xsdObject
                else:
                    xsdObjects[
                        'elem№' + str(xsdObjects.__len__() + 1)] = xsdObject

                tempTag = tag

                while tempTag is not None and \
                        (elementsGroup := next(
                            (tempTag.__dict__[innerTagName] for innerTagName in
                             tempTag.__dict__ if
                             innerTagName in ['group', 'all', 'choice', 'sequence']),
                            None)) is None:
                    tempTag = next(
                        (tempTag.__dict__[innerTagName] for innerTagName in
                         tempTag.__dict__ if
                         innerTagName in ['complexType', 'complexContent',
                                          'restriction', 'extension']), None)

                # if (innerTag := next(
                #         (tag.__dict__[innerTagName] for innerTagName in
                #          tag.__dict__ if
                #          innerTagName in ['complexType', 'complexContent',
                #                           # 'restriction', 'extension',
                #                           'group', 'all', 'choice', 'sequence']),
                #         None)) is not None:
                if elementsGroup is not None:
                    xsdObjects.update(self.parseElements(elementsGroup,
                                                         xsdObject.fullPath if hasattr(
                                                             xsdObject,
                                                             'fullPath') else parentPath))

                # if hasattr(tag, 'complexType'):
                #     xsdObjects.update(self.parseElements(tag.complexType, xsdObject.fullPath))
                # elif hasattr(tag, 'sequence'):
                #     xsdObjects.update(self.parseElements(tag.sequence, xsdObject.fullPath))

        # if 'properties' in xsdString:
        #     xsdProperties = xsdString['properties']
        #
        #     for prop in xsdProperties:
        #         xsdObjects.update(self.parseProperty(prop, xsdProperties, ''))
        #
        # if 'definitions' in xsdString:
        #     xsdProperties = xsdString['definitions']
        #
        #     for prop in xsdProperties:
        #         xsdObjects.update(self.parseProperty(prop, xsdProperties, '#/definitions'))

        return xsdObjects

    def parseProperty(self, propName, xsdPropertiesMap, pathPrefix) -> dict:
        xsdObjects = {}

        # propString = xsd.dumps(xsdPropertiesMap[propName], ensure_ascii=False)
        # print(propString)
        # propObject = xsd.loads(propString,object_hook=XsdParser.xsdPropertyDecoder)

        propObject = ''

        propObject.name = propName
        propObject.fullPath = pathPrefix + '/' + propName
        xsdObjects[propObject.fullPath] = propObject

        xsdObjects.update(self.checkInnerProperties(propObject))

        return xsdObjects

    def checkInnerProperties(self, propObject) -> dict:
        xsdObjects = {}

        if hasattr(propObject, 'oneOf') and propObject.oneOf:
            xsdObjects.update(
                self.parseCombinationKeywords(propObject, 'oneOf'))
        elif hasattr(propObject, 'anyOf') and propObject.anyOf:
            xsdObjects.update(
                self.parseCombinationKeywords(propObject, 'anyOf'))
        elif hasattr(propObject, 'allOf') and propObject.allOf:
            xsdObjects.update(
                self.parseCombinationKeywords(propObject, 'allOf'))
        elif hasattr(propObject, 'not') and propObject.__dict__['not']:
            xsdObjects.update(self.parseCombinationKeywords(propObject, 'not'))

        if hasattr(propObject, 'type'):
            if propObject.type == 'object' \
                    and hasattr(propObject, 'properties') \
                    and propObject.properties:
                xsdObjects.update(self.parseInnerProperties(propObject))
            elif propObject.type == 'array':
                xsdObjects.update(self.parseArrayItems(propObject))

        return xsdObjects

    def parseCombinationKeywords(self, propObject, keyword) -> dict:
        xsdObjects = {}

        if not hasattr(propObject, 'type'):
            propObject.type = keyword

        oneOfList = propObject.__dict__[keyword]
        for propIndex in range(len(oneOfList)):
            innerObject = oneOfList[propIndex]
            innerObject.fullPath = propObject.fullPath + '/' + \
                                   (innerObject.name if hasattr(innerObject,
                                                                'name')
                                    else keyword + '#' + str(propIndex + 1))
            xsdObjects[innerObject.fullPath] = innerObject

            xsdObjects.update(self.checkInnerProperties(innerObject))

        propObject.__dict__.pop(keyword)

        return xsdObjects

    def parseInnerProperties(self, propObject) -> dict:
        xsdObjects = {}

        innerProps = propObject.properties.__dict__
        for prop in innerProps:
            innerObject = innerProps[prop]

            if isinstance(innerObject, XsdPropertyObject):
                innerObject.name = prop
                innerObject.fullPath = propObject.fullPath + '/' + prop
                xsdObjects[innerObject.fullPath] = innerObject

                xsdObjects.update(self.checkInnerProperties(innerObject))

        propObject.__dict__.pop('properties')

        return xsdObjects

    def parseArrayItems(self, propArrayObject) -> dict:
        xsdObjects = {}

        if hasattr(propArrayObject, 'items'):

            itemsObject = propArrayObject.items

            if itemsObject:

                if hasattr(itemsObject, 'properties'):
                    arrayItems = itemsObject.properties.__dict__

                    for prop in arrayItems:
                        innerObject = arrayItems[prop]

                        if isinstance(innerObject, XsdPropertyObject):
                            innerObject.name = prop
                            innerObject.fullPath = propArrayObject.fullPath + '/' + prop
                            xsdObjects[innerObject.fullPath] = innerObject

                            xsdObjects.update(
                                self.checkInnerProperties(innerObject))

                else:
                    itemsObject.fullPath = propArrayObject.fullPath + '/' + \
                                           (itemsObject.name if hasattr(
                                               itemsObject,
                                               'name') else 'items')
                    xsdObjects[itemsObject.fullPath] = itemsObject

                    xsdObjects.update(self.checkInnerProperties(itemsObject))

                propArrayObject.items = 'Все элементы массива запаршены'

            else:
                propArrayObject.__dict__.pop('items')

        return xsdObjects
