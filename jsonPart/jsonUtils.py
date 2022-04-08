def isComplexType(jsonObject) -> bool:
    result = False

    if hasattr(jsonObject, 'type'):
        objectType = jsonObject.type

        # if not (objectType == 'string' or objectType == 'number' or objectType == 'integer'
        #         or objectType == 'boolean' or objectType == 'null'):
        if objectType == 'object':
            result = True

    return result
