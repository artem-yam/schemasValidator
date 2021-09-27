import json

from jsonPropertyObject import JsonPropertyObject


class JsonParser(object):

    def __init__(self, form):
        super().__init__()
        self.form = form

    def parseFileToText(self, filePath):
        jsonString = ''
        try:
            with open(filePath) as jsonFile:
                jsonString = json.load(jsonFile)
                jsonPrettyString = json.dumps(jsonString, indent=4)
                jsonFile.close()
        except Exception as err:
            print('Ошибки открытия файла: ', err)

        if jsonPrettyString is not None:
            jsonString = jsonPrettyString
            # print(jsonPrettyString)
            # self.form.textEditTextJson.append(jsonPrettyString)

        return jsonString

    def parseTextToObjects(self, jsonString):
        jsonObjects = []
        try:
            jsonString = json.loads(jsonString)
            jsonProperties = jsonString['properties']

            for prop in jsonProperties:
                propString = json.dumps(jsonProperties[prop])
                # print(propString)
                propObject = json.loads(propString,
                                        object_hook=JsonParser.jsonPropertyDecoder)
                propObject.name = prop
                # if not isinstance(propObject, list):
                #    propObject.name = prop
                # else:
                #    for obj in propObject:
                #        if obj.name:
                #            obj.name = prop
                jsonObjects.append(propObject)
                # jsonObjects.extend(propObject)

                if propObject.propType == 'object' and propObject.extraInfo['properties']:
                    innerProps = propObject.extraInfo['properties'].extraInfo
                    for prop in innerProps:
                        innerObject = innerProps[prop]
                        innerObject.name = prop
                        jsonObjects.append(innerObject)
                    propObject.extraInfo.pop('properties')

            print('\n'.join(map(str, jsonObjects)))

        except Exception as err:
            print('Ошибки получения объектов из json: ', err)
            print(err)
            jsonObjects = 'Ошибка преобразования json в объект, проверьте корректность загруженного текста'

        return jsonObjects

    @staticmethod
    def jsonPropertyDecoder(obj):
        # decodedObj = []
        # print(obj)

        if 'description' in obj:
            descriptionValue = obj['description']
            obj.pop('description')

        if 'type' in obj:
            typeValue = obj['type']
            obj.pop('type')

        decodedObj = JsonPropertyObject(None, None, descriptionValue if 'descriptionValue' in locals() else None,
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
