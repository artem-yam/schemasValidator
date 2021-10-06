import json
import sys
import traceback
from jsonPropertyObject import JsonPropertyObject


class JsonParser(object):
    # DEFINITIONS = []

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

    def parseTextToObjects(self, jsonString) -> dict:
        # JsonParser.DEFINITIONS = {}

        jsonObjects = {}
        try:
            jsonString = json.loads(jsonString)

            jsonObjects.update(self.parseProperties(jsonString))
            # jsonObjects.extend(self.parseDefinitions(jsonString))
            jsonObjects.update(self.parseDefinitions(jsonString))
            # jsonObjects.extend(self.parseProperties(jsonString))

            print('---------------------------------------------------')
            # print('\n'.join(map(str, jsonObjects.values())))

        except Exception as err:
            print('Ошибки получения объектов из json:\n', traceback.format_exc())
            jsonObjects = 'Ошибка преобразования json в объект, проверьте корректность загруженного текста'

        return jsonObjects

    def parseDefinitions(self, jsonString) -> dict:
        jsonObjects = {}

        if 'definitions' in jsonString:
            jsonProperties = jsonString['definitions']

            for prop in jsonProperties:
                propString = json.dumps(jsonProperties[prop], ensure_ascii=False)
                # print(propString)
                propObject = json.loads(propString,
                                        object_hook=JsonParser.jsonPropertyDecoder)
                propObject.name = prop
                propObject.fullPath = '/' + prop
                # jsonObjects.append(propObject)
                jsonObjects[propObject.fullPath] = propObject
                # JsonParser.DEFINITIONS[propObject.fullPath] = propObject
                # print('DEFINITIONS ' + str(JsonParser.DEFINITIONS))
                # print(propObject)

                if propObject.propType == 'object' and 'properties' in propObject.extraInfo:
                    innerProps = propObject.extraInfo['properties'].extraInfo
                    for prop in innerProps:
                        innerObject = innerProps[prop]
                        innerObject.name = prop
                        innerObject.fullPath += propObject.fullPath + '/' + prop
                        jsonObjects[innerObject.fullPath] = innerObject
                    propObject.extraInfo.pop('properties')

        return jsonObjects

    def parseProperties(self, jsonString) -> dict:
        jsonObjects = {}

        if 'properties' in jsonString:
            jsonProperties = jsonString['properties']

            for prop in jsonProperties:
                propString = json.dumps(jsonProperties[prop], ensure_ascii=False)
                # print(propString)
                propObject = json.loads(propString,
                                        object_hook=JsonParser.jsonPropertyDecoder)
                propObject.name = prop
                propObject.fullPath = '/' + prop
                # jsonObjects.append(propObject)
                jsonObjects[propObject.fullPath] = propObject

                if propObject.propType == 'object' and propObject.extraInfo['properties']:
                    innerProps = propObject.extraInfo['properties'].extraInfo
                    for prop in innerProps:
                        innerObject = innerProps[prop]
                        innerObject.name = prop
                        innerObject.fullPath += propObject.fullPath + '/' + prop
                        # jsonObjects.append(innerObject)
                        jsonObjects[innerObject.fullPath] = innerObject
                    propObject.extraInfo.pop('properties')

        return jsonObjects

    @staticmethod
    def jsonPropertyDecoder(obj):
        # if '$ref' in obj:
        # print('Obj ' + str(obj) + " has ref")
        # print('DEFINITIONS ' + str(JsonParser.DEFINITIONS))

        if 'description' in obj:
            descriptionValue = obj['description']
            obj.pop('description')

        if 'type' in obj:
            typeValue = obj['type']
            obj.pop('type')

        decodedObj = JsonPropertyObject(None, '', descriptionValue if 'descriptionValue' in locals() else None,
                                        typeValue if 'typeValue' in locals() else None, obj if obj else None)

        # print('obj = ' + str(obj))

        # if 'typeValue' in locals() and typeValue == 'object' and obj['properties']:
        #    if isinstance(obj['properties'], list):
        #        innerProps = obj['properties'][0].extraInfo
        #    else:
        #        innerProps = obj['properties'].extraInfo
        #    for prop in innerProps:
        #        propObject = innerProps[prop]
        #        propObject.name = prop
        #        decodedObj.append(propObject)

        return decodedObj
