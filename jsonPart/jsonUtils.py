def getElementSiblings(xsdElemObject, xsdObjectsDict) -> dict:
    resultDict = {}

    if hasattr(xsdElemObject, 'fullPath'):
        if (len(parentPath := xsdElemObject.fullPath.rpartition('/')[0]) > 0):
            for xsdObjectKey, xsdObject in xsdObjectsDict.items():
                if xsdObject != xsdElemObject \
                        and hasattr(xsdObject, 'fullPath') \
                        and xsdObject.fullPath.rpartition('/')[0] == parentPath:
                    resultDict[xsdObjectKey] = xsdObject

    return resultDict
