import json
import sys
import traceback
from copy import *

from jsonPart.jsonPropertyObject import JsonPropertyObject


class JsonParser(object):

    def __init__(self, form):
        super().__init__()
        self.form = form

    def parseFileToText(self, filePath) -> str:
        print("Url = " + filePath)
        jsonString = ''
        try:
            with open(filePath, encoding=sys.getfilesystemencoding()) as jsonFile:
                jsonString = json.load(jsonFile)
                jsonPrettyString = json.dumps(jsonString, indent=4, ensure_ascii=False)
                jsonFile.close()
        except BaseException as err:
            print('Ошибки открытия файла:\n', traceback.format_exc())

        if 'jsonPrettyString' in locals() and jsonPrettyString:
            jsonString = jsonPrettyString
            # print(jsonPrettyString)
            # self.form.textEditTextJson.append(jsonPrettyString)
        else:
            jsonString = 'Ошибка загрузки файла'

        return jsonString

    def getJsonDraftVersion(self, jsonString) -> str:
        try:
            jsonString = json.loads(jsonString)

            schemaDraft = jsonString['$schema']
            jsonString = schemaDraft

        except BaseException as err:
            print('Ошибки получения версии драфта:\n', traceback.format_exc())
            jsonString = 'Ошибка получения версии драфта'

        return jsonString

    def parseTextToObjects(self, jsonString) -> dict:
        jsonObjects = {}
        try:
            jsonString = json.loads(jsonString)

            jsonObjects.update(self.parseProperties(jsonString))

            print('---------------------------------------------------')
            print('Мапа ДО объединения')
            print('---------------------------------------------------')
            print(';\n'.join(map(str, jsonObjects.values())))

            jsonObjects = self.combineTypesWithElement(jsonObjects)

            print('---------------------------------------------------')
            print('Мапа ПОСЛЕ объединения')
            print('---------------------------------------------------')
            print(';\n'.join(map(str, jsonObjects.values())))

            if not jsonObjects:
                raise Exception("Объекты в json не обнаружены")

        except BaseException as err:
            print('Ошибки получения объектов из json:\n', traceback.format_exc())
            jsonObjects = 'Ошибка преобразования json в объект, проверьте корректность загруженного текста'

        return jsonObjects

    # TODO фикс на случай циклических ссылок
    def combineTypesWithElement(self, jsonObjects) -> dict:
        # TODO

        modifiedJsonObjects = copy(jsonObjects)

        typeObjectKey = self.getNextCustomTypeRefKey(modifiedJsonObjects)

        while typeObjectKey is not None:

            typeObject = modifiedJsonObjects[typeObjectKey]

            elemObjectKey = next(
                (elemObjectKey for elemObjectKey, elemObject
                 in modifiedJsonObjects.items() if
                 hasattr(elemObject, '$ref')
                 and typeObject.fullPath == elemObject.__dict__['$ref']),
                None)

            if elemObjectKey is None:
                modifiedJsonObjects.pop(typeObjectKey)
                typeObjectKey = self.getNextCustomTypeRefKey(modifiedJsonObjects)
            else:
                elemObject = modifiedJsonObjects[elemObjectKey]

                print(f'По типу: {typeObject.fullPath} смотрим элемент: {elemObject.fullPath}')

                itemsToAdd = {}

                copiedTypeObject = copy(typeObject)

                # TODO перенос полей

                typePath = copiedTypeObject.fullPath

                for fieldName in elemObject.__dict__:
                    if fieldName in ['name', 'fullPath']:
                        copiedTypeObject.__dict__[fieldName] = elemObject.__dict__[fieldName]

                jsonObjects[elemObjectKey] = copiedTypeObject
                modifiedJsonObjects[elemObjectKey] = copiedTypeObject

                # TODO копирование внутренних типов
                for innerTypeObjectKey, innerTypeObject in modifiedJsonObjects.items():
                    if innerTypeObject.fullPath.startswith(typePath + '/') and \
                            innerTypeObject.fullPath != typePath:
                        copiedInnerTypeObject = copy(innerTypeObject)

                        copiedInnerTypeObject.fullPath = copiedTypeObject.fullPath + '/' + \
                                                         innerTypeObject.fullPath.split(
                                                             typePath + '/')[1]

                        jsonObjects[
                            f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject
                        itemsToAdd[
                            f'element {copiedInnerTypeObject.fullPath}'] = copiedInnerTypeObject

                        print('Смотрим внутренний тип: ' + copiedInnerTypeObject.fullPath)

                modifiedJsonObjects.pop(elemObjectKey)
                modifiedJsonObjects.update(itemsToAdd)

        return jsonObjects

    def getNextCustomTypeRefKey(self, jsonObjects):
        # TODO вроде корректная проверка ссылки на тип, но надо проверить!!!
        for jsonObject in jsonObjects.values():
            if hasattr(jsonObject, '$ref'):
                typeObjectKey = next(
                    (typeObjectKey for typeObjectKey, typeObject in jsonObjects.items() if
                     typeObject.fullPath == jsonObject.__dict__['$ref']),
                    False)
                if typeObjectKey:
                    return typeObjectKey

        return None

    def parseProperties(self, jsonString) -> dict:
        jsonObjects = {}

        if 'properties' in jsonString:
            jsonProperties = jsonString['properties']

            for prop in jsonProperties:
                jsonObjects.update(self.parseProperty(prop, jsonProperties, ''))

        if 'definitions' in jsonString:
            jsonProperties = jsonString['definitions']

            for prop in jsonProperties:
                jsonObjects.update(self.parseProperty(prop, jsonProperties, '#/definitions'))

        return jsonObjects

    def parseProperty(self, propName, jsonPropertiesMap, pathPrefix) -> dict:
        jsonObjects = {}

        propString = json.dumps(jsonPropertiesMap[propName], ensure_ascii=False)
        # print(propString)
        propObject = json.loads(propString,
                                object_hook=JsonParser.jsonPropertyDecoder)
        propObject.name = propName
        propObject.fullPath = pathPrefix + '/' + propName
        jsonObjects[propObject.fullPath] = propObject

        jsonObjects.update(self.checkInnerProperties(propObject))

        return jsonObjects

    def checkInnerProperties(self, propObject) -> dict:
        jsonObjects = {}

        if hasattr(propObject, 'oneOf') and propObject.oneOf:
            jsonObjects.update(self.parseCombinationKeywords(propObject, 'oneOf'))
        elif hasattr(propObject, 'anyOf') and propObject.anyOf:
            jsonObjects.update(self.parseCombinationKeywords(propObject, 'anyOf'))
        elif hasattr(propObject, 'allOf') and propObject.allOf:
            jsonObjects.update(self.parseCombinationKeywords(propObject, 'allOf'))
        elif hasattr(propObject, 'not') and propObject.__dict__['not']:
            jsonObjects.update(self.parseCombinationKeywords(propObject, 'not'))

        if hasattr(propObject, 'type'):
            if propObject.type == 'object' \
                    and hasattr(propObject, 'properties') \
                    and propObject.properties:
                jsonObjects.update(self.parseInnerProperties(propObject))
            elif propObject.type == 'array':
                jsonObjects.update(self.parseArrayItems(propObject))

        return jsonObjects

    def parseCombinationKeywords(self, propObject, keyword) -> dict:
        jsonObjects = {}

        if not hasattr(propObject, 'type'):
            propObject.type = keyword

        oneOfList = propObject.__dict__[keyword]
        for propIndex in range(len(oneOfList)):
            innerObject = oneOfList[propIndex]
            innerObject.fullPath = propObject.fullPath + '/' + \
                                   (innerObject.name if hasattr(innerObject, 'name')
                                    else keyword + '#' + str(propIndex + 1))
            jsonObjects[innerObject.fullPath] = innerObject

            jsonObjects.update(self.checkInnerProperties(innerObject))

        propObject.__dict__.pop(keyword)

        return jsonObjects

    def parseInnerProperties(self, propObject) -> dict:
        jsonObjects = {}

        innerProps = propObject.properties.__dict__
        for prop in innerProps:
            innerObject = innerProps[prop]

            if isinstance(innerObject, JsonPropertyObject):
                innerObject.name = prop
                innerObject.fullPath = propObject.fullPath + '/' + prop
                jsonObjects[innerObject.fullPath] = innerObject

                jsonObjects.update(self.checkInnerProperties(innerObject))

        propObject.__dict__.pop('properties')

        return jsonObjects

    def parseArrayItems(self, propArrayObject) -> dict:
        jsonObjects = {}

        if hasattr(propArrayObject, 'items'):

            # itemsObject = propArrayObject.items
            itemsList = propArrayObject.items \
                if isinstance(propArrayObject.items, list) \
                else [propArrayObject.items]

            itemsParsed = False

            for itemsObject in itemsList:

                if itemsObject \
                        and isinstance(itemsObject, JsonPropertyObject) \
                        and not itemsObject.isEmpty():
                    if not itemsParsed:
                        itemsParsed = True

                    if hasattr(itemsObject, 'properties'):
                        arrayItems = itemsObject.properties.__dict__

                        for prop in arrayItems:
                            innerObject = arrayItems[prop]

                            if isinstance(innerObject, JsonPropertyObject):
                                innerObject.name = prop
                                innerObject.fullPath = propArrayObject.fullPath + '/' + prop
                                jsonObjects[innerObject.fullPath] = innerObject

                                jsonObjects.update(self.checkInnerProperties(innerObject))

                    else:
                        itemsObject.fullPath = propArrayObject.fullPath + '/' + \
                                               (itemsObject.name if hasattr(itemsObject, 'name') else 'items')
                        jsonObjects[itemsObject.fullPath] = itemsObject

                        jsonObjects.update(self.checkInnerProperties(itemsObject))

            if itemsParsed:
                propArrayObject.items = 'Все элементы массива запаршены'
            else:
                propArrayObject.__dict__.pop('items')

        return jsonObjects

    @staticmethod
    def jsonPropertyDecoder(obj):
        return JsonPropertyObject(obj)
