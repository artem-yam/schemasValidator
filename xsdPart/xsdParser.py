import re
import sys
import traceback
from copy import *
from xml.dom.minidom import parseString

from lxml import objectify

from xsdPart.xsdPropertyObject import XsdPropertyObject
from xsdPart.xsdUtils import *


class XsdParser(object):

    def __init__(self, form):
        super().__init__()
        self.form = form

    def parseFileToText(self, filePath) -> str:
        logging.info("Url = " + filePath)
        xsdString = 'Ошибка загрузки файла'
        try:
            with open(filePath,
                      encoding=sys.getfilesystemencoding()) as xsdFile:
                xml = xsdFile.read()
                xsdFile.close()
        except BaseException as err:
            logging.warning('Ошибки открытия файла:\n', traceback.format_exc())

        if 'xml' in locals():
            try:
                # from yattag import indent
                # xsdString = indent(xml, indentation=4 * ' ')

                # from xml.dom.minidom import parseString
                xsdString = '\n'.join(
                    [line for line in
                     parseString(xml).toprettyxml(indent=4 * ' ').split('\n') if
                     line.strip()])
            except BaseException as err:
                logging.warning('Ошибки загрузки файла:\n',
                                traceback.format_exc())

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
                    referedElement = copy(
                        xsdObjects[f'element /{xsdObject.ref}'])
                    xsdObjects[objectKey] = referedElement
                    for fieldName in xsdObject.__dict__:
                        if fieldName not in ['tag', 'type', 'ref']:
                            referedElement.__dict__[fieldName] = \
                                xsdObject.__dict__[fieldName]

            # logging.info('---------------------------------------------------')
            # logging.info('Мапа ДО объединения')
            # logging.info('---------------------------------------------------')
            # logging.info(';\n'.join(map(str, xsdObjects.values())))

            xsdObjects = self.processSimpleTypesChain(xsdObjects)
            # xsdObjects = self.processExtensionsAndRestrictions(xsdObjects)

            logging.info('---------------------------------------------------')
            logging.info('Мапа ДО объединения')
            logging.info('---------------------------------------------------')
            logging.info(';\n'.join(map(str, xsdObjects.values())))

            xsdObjects = self.processExtensionsAndRestrictions(xsdObjects)
            # xsdObjects = self.combineTypesWithElement(xsdObjects)

            logging.info('---------------------------------------------------')
            logging.info('Мапа ПОСЛЕ объединения')
            logging.info('---------------------------------------------------')
            logging.info(';\n'.join(map(str, xsdObjects.values())))

            if not xsdObjects:
                raise Exception("Объекты в xsd не обнаружены")

        except BaseException as err:
            logging.warning('Ошибки получения объектов из xsd:\n',
                            traceback.format_exc())
            xsdObjects = 'Ошибка преобразования xsd в объект,' \
                         + ' проверьте корректность загруженного текста'

        return xsdObjects

    # TODO фикс на случай циклических ссылок
    def processSimpleTypesChain(self, xsdObjects) -> dict:
        modifiedXsdObjects = copy(xsdObjects)

        # for typeObjectKey, typeObject in modifiedXsdObjects.items():
        while True:
            typeObjectKey = next(
                (typeObjectKey for typeObjectKey, typeObject in
                 modifiedXsdObjects.items() if
                 typeObject.tag == 'simpleType' and not next(
                     (objectKey for objectKey, xsdObject in
                      modifiedXsdObjects.items() if
                      xsdObject.tag == 'simpleType' and typeObject.type == xsdObject.name),
                     False)),
                False)

            if not typeObjectKey:
                break

            typeObject = modifiedXsdObjects[typeObjectKey]
            modifiedXsdObjects.pop(typeObjectKey)

            while True:
                elemObjectKey = next(
                    (objectKey for objectKey, xsdObject in
                     modifiedXsdObjects.items() if
                     typeObject.name == xsdObject.type), False)

                if not elemObjectKey:
                    break

                elemObject = modifiedXsdObjects[elemObjectKey]
                modifiedXsdObjects.pop(elemObjectKey)

                copiedTypeObject = copy(typeObject)

                for fieldName in elemObject.__dict__:
                    if fieldName not in ['type']:
                        copiedTypeObject.__dict__[fieldName] = \
                            elemObject.__dict__[fieldName]

                modifiedXsdObjects[elemObjectKey] = copiedTypeObject
                xsdObjects[elemObjectKey] = copiedTypeObject

        # return modifiedXsdObjects
        return xsdObjects

    def processExtensionsAndRestrictions(self, xsdObjects) -> dict:
        modifiedXsdObjects = copy(xsdObjects)

        # xsdObjectKey == 'extension /permission/attrs'
        # xsdObject.name == 'attrs' and hasattr(xsdObject, 'tag') and xsdObject.tag == 'extension'
        for xsdObjectKey, xsdObject in xsdObjects.items():
            if hasattr(xsdObject, 'tag') and xsdObject.tag == 'extension' \
                    and hasattr(xsdObject, 'base') \
                    and (typeObjectKey := self.getTypeObjectKeyByName(
                            xsdObjects, xsdObject.base)):
                itemsToUpdate = self.proccessObjectRef(modifiedXsdObjects,
                                                       xsdObjectKey,
                                                       typeObjectKey)

                modifiedXsdObjects.update(itemsToUpdate)
                # xsdObjects.update(itemsToUpdate)
                # modifiedXsdObjects.pop(xsdObjectKey)

        return modifiedXsdObjects

    def getTypeObjectKeyByName(self, xsdObjects, typeName):
        return next(
            (typeObjectKey for typeObjectKey, typeObject in
             xsdObjects.items() if
             typeObject.name.lower() == typeName.lower()
             and (typeObjectKey.startswith('complexType')
                  or typeObjectKey.startswith('simpleType'))),
            None)

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
                 # TODO хз, нужно ли убирать сравнение по тегу???
                 elemObject.tag == 'element' and
                 typeObject.name == elemObject.type), None)

            if elemObjectKey is None:
                modifiedXsdObjects.pop(typeObjectKey)
                typeObjectKey = self.getNextCustomTypeRefKey(modifiedXsdObjects)
            else:
                # logging.info(
                #     f'По типу: {typeObject.fullPath} смотрим элемент: '
                #     f'{modifiedXsdObjects[elemObjectKey].fullPath}')

                # elemObject = modifiedXsdObjects[elemObjectKey]
                #
                # itemsToAdd = {}
                #
                # copiedTypeObject = copy(typeObject)
                #
                # # TODO перенос полей
                #
                # typePath = copiedTypeObject.fullPath
                #
                # for fieldName in elemObject.__dict__:
                #     if fieldName in ['name', 'fullPath', 'tag']:
                #         copiedTypeObject.__dict__[fieldName] = \
                #             elemObject.__dict__[fieldName]
                #
                # xsdObjects[elemObjectKey] = copiedTypeObject
                #
                # modifiedXsdObjects[elemObjectKey] = copiedTypeObject
                #
                # # TODO копирование внутренних типов
                # for innerTypeObjectKey, innerTypeObject in modifiedXsdObjects.items():
                #     if innerTypeObject.fullPath.startswith(typePath + '/') and \
                #             innerTypeObject.fullPath != typePath:
                #         copiedInnerTypeObject = copy(innerTypeObject)
                #
                #         copiedInnerTypeObject.fullPath = copiedTypeObject.fullPath + '/' + \
                #                                          innerTypeObject.fullPath.split(
                #                                              typePath + '/')[1]
                #
                #         xsdObjects[
                #             f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject
                #         itemsToAdd[
                #             f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject
                #
                #         logging.info(
                #             'Смотрим внутренний тип: ' + copiedInnerTypeObject.fullPath)
                #
                # modifiedXsdObjects.pop(elemObjectKey)
                # modifiedXsdObjects.update(itemsToAdd)

                itemsToUpdate = self.proccessObjectRef(modifiedXsdObjects,
                                                       elemObjectKey,
                                                       typeObjectKey)

                modifiedXsdObjects.update(itemsToUpdate)
                xsdObjects.update(itemsToUpdate)
                modifiedXsdObjects.pop(elemObjectKey)

        return xsdObjects

    def proccessObjectRef(self, xsdObjects, originalObjectKey,
                          destinationObjectKey) -> dict:
        itemsToAdd = {}
        xsdObjectsTempCopy = copy(xsdObjects)
        originalObject = xsdObjects[originalObjectKey]
        destinationObject = xsdObjects[destinationObjectKey]

        copiedDestinationObject = copy(destinationObject)

        destinationObjectPath = copiedDestinationObject.fullPath

        for fieldName in originalObject.__dict__:
            if fieldName in ['name', 'fullPath', 'tag']:
                copiedDestinationObject.__dict__[fieldName] = \
                    originalObject.__dict__[fieldName]

        itemsToAdd[originalObjectKey] = copiedDestinationObject

        xsdObjectsTempCopy[originalObjectKey] = copiedDestinationObject

        # TODO копирование внутренних типов
        for innerTypeObjectKey, innerTypeObject in xsdObjectsTempCopy.items():
            if innerTypeObject.fullPath.startswith(
                    destinationObjectPath + '/') and \
                    innerTypeObject.fullPath != destinationObjectPath:
                copiedInnerTypeObject = copy(innerTypeObject)

                copiedInnerTypeObject.fullPath = copiedDestinationObject.fullPath + '/' + \
                                                 innerTypeObject.fullPath.split(
                                                     destinationObjectPath + '/')[
                                                     1]

                itemsToAdd[
                    f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject

                # logging.info(
                #     f'Обновили внутренний тип: из {innerTypeObject.fullPath}'
                #     f' в {copiedInnerTypeObject.fullPath}')

        return itemsToAdd

    def getNextCustomTypeRefKey(self, xsdObjects):
        # TODO вроде корректная проверка ссылки на тип, но надо проверить!!!
        for xsdObject in xsdObjects.values():
            typeObjectKey = next(
                (typeObjectKey for typeObjectKey, typeObject in
                 xsdObjects.items() if
                 typeObject.name == xsdObject.type
                 and typeObject.type.lower() not in XSD_SIMPLE_TYPES
                 # and typeObject.tag not in ['element', 'attribute']),
                 and typeObject.tag not in ['element']),
                # and typeObject.tag != 'element'),
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
    #     for xsdObject in xsdObjects.values():
    #         if hasattr(xsdObject, 'type') and \
    #                 next((typeObject for typeObject in xsdObjects.values() if
    #                       typeObject.name == xsdObject.type), False):
    #             return True
    #     return False

    def parseAttributeAsElement(self, schemaTag, parentPath,
                                attributeIndex) -> dict:
        xsdObjects = {}

        xsdObject = XsdPropertyObject(schemaTag, parentPath, xsdObjects)

        if not hasattr(xsdObject, 'name'):
            xsdObject.name = 'attribute№' + str(attributeIndex + 1)

        xsdObject.fullPath = parentPath + '/' + xsdObject.name

        xsdObjects[f'{xsdObject.tag} {xsdObject.fullPath}'] = xsdObject

        return xsdObjects

    def parseElements(self, schemaTag, parentPath) -> dict:
        xsdObjects = {}

        for tag in schemaTag.iterchildren():

            # TODO парсинг аттрибутов в отдельные элементы
            if hasattr(tag, 'attribute'):
                for i in range(len(tag.attribute)):
                    attribute = tag.attribute[i]

                    if hasattr(tag, 'attrib') and 'name' in tag.attrib:
                        tagPath = parentPath + '/' + tag.attrib['name']
                    elif hasattr(tag, 'attrib') and 'base' in tag.attrib:
                        tagPath = parentPath + '/' + getStringWithoutNamespace(
                            tag.attrib['base'])
                    else:
                        # tagPath = parentPath + '/someTag'
                        tagPath = parentPath

                    # if hasattr(attribute, 'attrib') \
                    #         and 'name' in attribute.attrib:
                    #     attributePath = tagPath + '/' + attribute.attrib['name']
                    # else:
                    #     attributePath = tagPath + '/attribute№' + str(i + 1)

                    xsdObjects.update(
                        self.parseAttributeAsElement(attribute, tagPath, i))

            if re.search('(group|all|choice|sequence)$', tag.tag,
                         re.IGNORECASE):
                # for innerTag in schemaTag.iterchildren():
                #     xsdObjects.update(self.parseElements(innerTag, parentPath))
                xsdObjects.update(self.parseElements(tag, parentPath))
            elif hasattr(tag, 'element'):
                xsdObjects.update(self.parseElements(tag.element, parentPath))
            else:
                xsdObject = XsdPropertyObject(tag, parentPath, xsdObjects)

                # if not hasattr(xsdObject, 'name'):
                #     xsdObject.name = 'elem№' + str(xsdObjects.__len__() + 1)
                #
                # xsdObject.fullPath = parentPath + '/' + xsdObject.name

                if hasattr(tag, 'complexContent'):
                    tag.complexContent.attrib['name'] = xsdObject.name
                    xsdObjects.update(self.parseElements(tag.complexContent,
                                                         parentPath + '/' + xsdObject.name))
                elif hasattr(tag, 'simpleContent'):
                    tag.simpleContent.attrib['name'] = xsdObject.name
                    xsdObjects.update(self.parseElements(tag.simpleContent,
                                                         parentPath + '/' + xsdObject.name))

                # else:

                # xsdObjects[xsdObject.fullPath] = xsdObject
                xsdObjects[f'{xsdObject.tag} {xsdObject.fullPath}'] = xsdObject

                tempTag = tag

                # next(tempTag.itersiblings())

                while tempTag is not None and \
                        (elementsGroup := next(
                            (tempTag.__dict__[innerTagName] for innerTagName in
                             tempTag.__dict__ if
                             innerTagName in ['group', 'all', 'choice',
                                              'sequence']),
                            None)) is None:
                    tempTag = next(
                        (tempTag.__dict__[innerTagName] for innerTagName in
                         tempTag.__dict__ if
                         innerTagName in ['complexType', 'complexContent',
                                          'restriction', 'extension']), None)

                if elementsGroup is not None:
                    xsdObjects.update(self.parseElements(elementsGroup,
                                                         xsdObject.fullPath if hasattr(
                                                             xsdObject,
                                                             'fullPath') else parentPath))

                # TODO подумать над этим фрагментом (тест на типе permission)

                # if (innerTag := next(
                #         (tag.__dict__[innerTagName] for innerTagName in
                #          tag.__dict__ if
                #          innerTagName in ['complexType', 'complexContent',
                #                           # 'restriction', 'extension',
                #                           'group', 'all', 'choice', 'sequence']),
                #         None)) is not None:
                #     xsdObjects.update(self.parseElements(tag, xsdObject.fullPath))

                # TODO конец фрагмента

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
        # logging.info(propString)
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
            xsdObjects[
                f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

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
                xsdObjects[
                    f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

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
                            xsdObjects[
                                f'{innerObject.tag} {innerObject.fullPath}'] = innerObject

                            xsdObjects.update(
                                self.checkInnerProperties(innerObject))

                else:
                    itemsObject.fullPath = propArrayObject.fullPath + '/' + \
                                           (itemsObject.name if hasattr(
                                               itemsObject,
                                               'name') else 'items')
                    # xsdObjects[itemsObject.fullPath] = itemsObject
                    xsdObjects[
                        f'{itemsObject.tag} {itemsObject.fullPath}'] = itemsObject

                    xsdObjects.update(self.checkInnerProperties(itemsObject))

                propArrayObject.items = 'Все элементы массива запаршены'

            else:
                propArrayObject.__dict__.pop('items')

        return xsdObjects
