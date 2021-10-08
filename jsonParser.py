import json
import sys
import traceback
from jsonPropertyObject import JsonPropertyObject


class JsonParser(object):

    def __init__(self, form):
        super().__init__()
        self.form = form

    def parseFileToText(self, filePath) -> str:
        jsonString = ''
        try:
            with open(filePath, encoding=sys.getfilesystemencoding()) as jsonFile:
                jsonString = json.load(jsonFile)
                jsonPrettyString = json.dumps(jsonString, indent=4, ensure_ascii=False)
                jsonFile.close()
        except Exception as err:
            print('Ошибки открытия файла:\n', traceback.format_exc())

        if jsonPrettyString is not None:
            jsonString = jsonPrettyString
            # print(jsonPrettyString)
            # self.form.textEditTextJson.append(jsonPrettyString)

        return jsonString

    def getJsonDraftVersion(self, jsonString) -> str:
        jsonString = json.loads(jsonString)

        try:
            schemaDraft = jsonString['$schema']
            jsonString = schemaDraft

        except Exception as err:
            print('Ошибки получения версии драфта:\n', traceback.format_exc())
            jsonString = 'Ошибка получения версии драфта'

        return jsonString

    def parseTextToObjects(self, jsonString) -> dict:
        jsonObjects = {}
        try:
            jsonString = json.loads(jsonString)

            jsonObjects.update(self.parseProperties(jsonString))

            print('---------------------------------------------------')
            print(';\n'.join(map(str, jsonObjects.values())))

        except Exception as err:
            print('Ошибки получения объектов из json:\n', traceback.format_exc())
            jsonObjects = 'Ошибка преобразования json в объект, проверьте корректность загруженного текста'

        return jsonObjects

    def parseProperties(self, jsonString) -> dict:
        jsonObjects = {}

        if 'properties' in jsonString:
            jsonProperties = jsonString['properties']

            for prop in jsonProperties:
                jsonObjects.update(self.parseProperty(prop, jsonProperties))

        if 'definitions' in jsonString:
            jsonProperties = jsonString['definitions']

            for prop in jsonProperties:
                jsonObjects.update(self.parseProperty(prop, jsonProperties))

        return jsonObjects

    def parseProperty(self, propName, jsonPropertiesMap):
        jsonObjects = {}

        propString = json.dumps(jsonPropertiesMap[propName], ensure_ascii=False)
        # print(propString)
        propObject = json.loads(propString,
                                object_hook=JsonParser.jsonPropertyDecoder)
        propObject.name = propName
        propObject.fullPath = '/' + propName
        jsonObjects[propObject.fullPath] = propObject

        jsonObjects.update(self.checkInnerProperties(propObject))

        return jsonObjects

    def checkInnerProperties(self, propObject) -> dict:
        jsonObjects = {}

        if hasattr(propObject, 'extraInfo') and propObject.extraInfo:
            if 'oneOf' in propObject.extraInfo \
                    and propObject.extraInfo['oneOf']:
                jsonObjects.update(self.parseOneOf(propObject))

            if propObject.propType == 'object' \
                    and 'properties' in propObject.extraInfo \
                    and propObject.extraInfo['properties']:
                jsonObjects.update(self.parseInnerProperties(propObject))
            elif propObject.propType == 'array' \
                    and 'items' in propObject.extraInfo \
                    and propObject.extraInfo['items']:
                jsonObjects.update(self.parseArrayItems(propObject))

        return jsonObjects

    def parseOneOf(self, propObject) -> dict:
        jsonObjects = {}

        oneOfList = propObject.extraInfo['oneOf']
        for propIndex in range(len(oneOfList)):
            # for prop in oneOfList:
            innerObject = oneOfList[propIndex]
            innerObject.fullPath += propObject.fullPath + '/' + \
                                    (innerObject.name if innerObject.name else 'oneOf#' + str(propIndex + 1))
            jsonObjects[innerObject.fullPath] = innerObject

            jsonObjects.update(self.checkInnerProperties(innerObject))

        propObject.extraInfo.pop('oneOf')

        return jsonObjects

    def parseInnerProperties(self, propObject) -> dict:
        jsonObjects = {}

        innerProps = propObject.extraInfo['properties'].extraInfo
        for prop in innerProps:
            innerObject = innerProps[prop]
            innerObject.name = prop
            innerObject.fullPath += propObject.fullPath + '/' + prop
            jsonObjects[innerObject.fullPath] = innerObject

            jsonObjects.update(self.checkInnerProperties(innerObject))

        propObject.extraInfo.pop('properties')

        return jsonObjects

    def parseArrayItems(self, propArrayObject) -> dict:
        jsonObjects = {}

        # if 'items' in propObject.extraInfo and propObject.extraInfo['items']:

        itemsObject = propArrayObject.extraInfo['items']

        if itemsObject.propType == 'object':
            arrayItems = itemsObject.extraInfo['properties'].extraInfo

            for prop in arrayItems:
                innerObject = arrayItems[prop]
                innerObject.name = prop
                innerObject.fullPath += propArrayObject.fullPath + '/' + prop
                jsonObjects[innerObject.fullPath] = innerObject

                jsonObjects.update(self.checkInnerProperties(innerObject))

            # propArrayObject.extraInfo.pop('items')
        elif isinstance(itemsObject, JsonPropertyObject):
            itemsObject.fullPath += propArrayObject.fullPath + '/' + \
                                    (itemsObject.name if itemsObject.name else 'items')
            jsonObjects[itemsObject.fullPath] = itemsObject

            jsonObjects.update(self.checkInnerProperties(itemsObject))
            # propArrayObject.extraInfo.pop('items')

        # propArrayObject.extraInfo.pop('items')
        propArrayObject.extraInfo['items'] = 'Все элементы массива запаршены'

        return jsonObjects

    @staticmethod
    def jsonPropertyDecoder(obj):
        return JsonPropertyObject(obj)
