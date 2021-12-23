import sys
import traceback
from copy import *
from xml.dom.minidom import parseString

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
            # xsdStringEncode = xsdString.encode()
            rootSchemaTag = objectify.fromstring(xsdString.encode())
            # rootSchemaTag2 = untangle.parse(xsdString)

            xsdObjects.update(self.parseElements(rootSchemaTag, ''))

            # xsdObjectsCopy = xsdObjects.copy()

            for objectKey in xsdObjects:
                xsdObject = xsdObjects[objectKey]
                if hasattr(xsdObject, 'ref'):
                    # referedElement = deepcopy(xsdObjects[f'element /{xsdObject.ref}'])
                    referedElement = copy(xsdObjects[f'element /{xsdObject.ref}'])
                    xsdObjects[objectKey] = referedElement
                    for fieldName in xsdObject.__dict__:
                        if fieldName not in ['tag', 'type', 'ref']:
                            referedElement.__dict__[fieldName] = xsdObject.__dict__[fieldName]

            print('---------------------------------------------------')
            print('Мапа ДО объединения')
            print('---------------------------------------------------')
            print(';\n'.join(map(str, xsdObjects.values())))

            xsdObjects = self.processSimplyTypesChain(xsdObjects)
            xsdObjects = self.combineTypesWithElement(xsdObjects)

            print('---------------------------------------------------')
            print('Мапа ПОСЛЕ объединения')
            print('---------------------------------------------------')
            print(';\n'.join(map(str, xsdObjects.values())))

            if not xsdObjects:
                raise Exception("Объекты в xsd не обнаружены")

        except Exception as err:
            print('Ошибки получения объектов из xsd:\n', traceback.format_exc())
            xsdObjects = 'Ошибка преобразования xsd в объект, проверьте корректность загруженного текста'

        return xsdObjects

    # TODO фикс на случай циклических ссылок
    def processSimplyTypesChain(self, xsdObjects) -> dict:
        modifiedXsdObjects = copy(xsdObjects)

        # for typeObjectKey, typeObject in modifiedXsdObjects.items():
        while True:
            typeObjectKey = next(
                (typeObjectKey for typeObjectKey, typeObject in modifiedXsdObjects.items() if
                 typeObject.tag == 'simpleType' and not next(
                     (objectKey for objectKey, object in modifiedXsdObjects.items() if
                      object.tag == 'simpleType' and typeObject.type == object.name),
                     False)),
                False)

            if not typeObjectKey:
                break

            typeObject = modifiedXsdObjects[typeObjectKey]
            modifiedXsdObjects.pop(typeObjectKey)

            while True:
                elemObjectKey = next(
                    (objectKey for objectKey, object in modifiedXsdObjects.items() if
                     typeObject.name == object.type), False)

                if not elemObjectKey:
                    break

                elemObject = modifiedXsdObjects[elemObjectKey]
                modifiedXsdObjects.pop(elemObjectKey)

                copiedTypeObject = copy(typeObject)

                for fieldName in elemObject.__dict__:
                    if fieldName not in ['type']:
                        copiedTypeObject.__dict__[fieldName] = elemObject.__dict__[fieldName]

                modifiedXsdObjects[elemObjectKey] = copiedTypeObject
                xsdObjects[elemObjectKey] = copiedTypeObject

        # return modifiedXsdObjects
        return xsdObjects

    # TODO фикс на случай циклических ссылок
    def combineTypesWithElement(self, xsdObjects) -> dict:
        # TODO

        # modifiedXsdObjects = deepcopy(xsdObjects)
        modifiedXsdObjects = copy(xsdObjects)

        typeObjectKey = self.getNextCustomTypeRefKey(modifiedXsdObjects)

        # while self.hasCustomTypeRef(modifiedXsdObjects):
        while typeObjectKey is not None:

            typeObject = modifiedXsdObjects[typeObjectKey]

            elemObjectKey = next(
                (elemObjectKey for elemObjectKey, elemObject
                 in modifiedXsdObjects.items() if
                 # elemObject.tag == 'element' and
                 typeObject.name == elemObject.type), None)

            if elemObjectKey is None:
                modifiedXsdObjects.pop(typeObjectKey)
                typeObjectKey = self.getNextCustomTypeRefKey(modifiedXsdObjects)
            else:
                elemObject = modifiedXsdObjects[elemObjectKey]

                print(f'По типу: {typeObject.fullPath} смотрим элемент: {elemObject.fullPath}')

                # itemsToRemove = []
                itemsToAdd = {}
                # typeObject = False

                # copiedTypeObject = deepcopy(typeObject)
                copiedTypeObject = copy(typeObject)

                # modifiedXsdObjects[elemObjectKey] = copiedTypeObject

                # TODO перенос полей

                # typeName = copiedTypeObject.name
                typePath = copiedTypeObject.fullPath

                for fieldName in elemObject.__dict__:
                    if fieldName in ['name', 'fullPath', 'tag']:
                        copiedTypeObject.__dict__[fieldName] = elemObject.__dict__[fieldName]

                xsdObjects[elemObjectKey] = copiedTypeObject
                # itemsToAdd[elemObjectKey] = copiedTypeObject
                modifiedXsdObjects[elemObjectKey] = copiedTypeObject

                # modifiedXsdObjects.pop(elemObjectKey)
                # itemsToRemove.append(elemObjectKey)

                # modifiedXsdObjects.pop(elemObjectKey)

                # TODO копирование внутренних типов
                for innerTypeObjectKey, innerTypeObject in modifiedXsdObjects.items():
                    if innerTypeObject.fullPath.startswith(typePath) and \
                            innerTypeObject.fullPath != typePath:
                        # copiedInnerTypeObject = deepcopy(innerTypeObject)
                        copiedInnerTypeObject = copy(innerTypeObject)

                        copiedInnerTypeObject.fullPath = copiedTypeObject.fullPath + \
                                                         innerTypeObject.fullPath.split(
                                                             typePath)[1]

                        xsdObjects[
                            f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject
                        itemsToAdd[
                            f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject

                        print('Смотрим внутренний тип: ' + copiedInnerTypeObject.fullPath)

                modifiedXsdObjects.pop(elemObjectKey)
                modifiedXsdObjects.update(itemsToAdd)

        # modifiedXsdObjects = deepcopy(xsdObjects)
        # modifiedXsdObjects = copy(xsdObjects)

        # modifiedXsdObjects.update(itemsToAdd)
        # for itemToRemove in itemsToRemove:
        #     modifiedXsdObjects.pop(itemToRemove)

        return xsdObjects

    def getNextCustomTypeRefKey(self, xsdObjects):
        # TODO вроде корректная проверка ссылки на тип, но надо проверить!!!
        for object in xsdObjects.values():
            typeObjectKey = next(
                (typeObjectKey for typeObjectKey, typeObject in xsdObjects.items() if
                 typeObject.name == object.type and typeObject.tag != 'element'),
                False)
            if typeObjectKey:
                return typeObjectKey

        return None

    # TODO это другой алгоритм объединения элементов со связанными типами
    # def combineTypesWithElement(self, xsdObjects) -> dict:
    #     modifiedXsdObjects = copy(xsdObjects)
    #
    #     itemsToRemove = []
    #
    #     while self.hasCustomTypeRef(modifiedXsdObjects):
    #
    #         for elemObjectKey, elemObject in modifiedXsdObjects.items():
    #
    #             typeObject = next((typeObject for typeObject in modifiedXsdObjects.values() if
    #                                typeObject.name == elemObject.type), False)
    #             if typeObject:
    #                 copiedTypeObject = copy(typeObject)
    #
    #                 typePath = copiedTypeObject.fullPath
    #
    #                 for fieldName in elemObject.__dict__:
    #                     if fieldName in ['name', 'fullPath', 'tag']:
    #                         copiedTypeObject.__dict__[fieldName] = elemObject.__dict__[fieldName]
    #
    #                 xsdObjects[elemObjectKey] = copiedTypeObject
    #
    #                 itemsToRemove.append(elemObjectKey)
    #
    #                 for innerTypeObjectKey, innerTypeObject in modifiedXsdObjects.items():
    #                     if innerTypeObject.fullPath.startswith(typePath) and \
    #                             innerTypeObject.fullPath != typePath:
    #                         copiedInnerTypeObject = copy(innerTypeObject)
    #
    #                         copiedInnerTypeObject.fullPath = copiedTypeObject.fullPath + \
    #                                                          innerTypeObject.fullPath.split(
    #                                                              typePath)[1]
    #
    #                         xsdObjects[
    #                             f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject
    #
    #         modifiedXsdObjects = copy(xsdObjects)
    #         for itemToRemove in itemsToRemove:
    #             modifiedXsdObjects.pop(itemToRemove)
    #
    #     return xsdObjects
    #
    # def hasCustomTypeRef(self, xsdObjects) -> bool:
    #     for object in xsdObjects.values():
    #         if hasattr(object, 'type') and \
    #                 next((typeObject for typeObject in xsdObjects.values() if
    #                       typeObject.name == object.type), False):
    #             return True
    #     return False

    def parseElements(self, schemaTag, parentPath) -> dict:
        xsdObjects = {}

        for tag in schemaTag.iterchildren():
            if hasattr(tag, 'element'):
                xsdObjects.update(self.parseElements(tag.element, parentPath))
            else:
                xsdObject = XsdPropertyObject(tag)

                if not hasattr(xsdObject, 'name'):
                    xsdObject.name = 'elem№' + str(xsdObjects.__len__() + 1)

                xsdObject.fullPath = parentPath + '/' + xsdObject.name

                # xsdObjects[xsdObject.fullPath] = xsdObject
                xsdObjects[f'{xsdObject.tag} {xsdObject.fullPath}'] = xsdObject

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
        # xsdObjects[propObject.fullPath] = propObject
        xsdObjects[f'{propObject.tag} {propObject.fullPath}'] = propObject

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
            # xsdObjects[innerObject.fullPath] = innerObject
            xsdObjects[f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

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
                # xsdObjects[innerObject.fullPath] = innerObject
                xsdObjects[f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

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
                            # xsdObjects[innerObject.fullPath] = innerObject
                            xsdObjects[f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

                            xsdObjects.update(
                                self.checkInnerProperties(innerObject))

                else:
                    itemsObject.fullPath = propArrayObject.fullPath + '/' + \
                                           (itemsObject.name if hasattr(
                                               itemsObject,
                                               'name') else 'items')
                    # xsdObjects[itemsObject.fullPath] = itemsObject
                    xsdObjects[f'{itemsObject.tag} {itemsObject.fullPath}'] = itemsObject

                    xsdObjects.update(self.checkInnerProperties(itemsObject))

                propArrayObject.items = 'Все элементы массива запаршены'

            else:
                propArrayObject.__dict__.pop('items')

        return xsdObjects
