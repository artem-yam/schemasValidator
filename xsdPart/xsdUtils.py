XSD_SIMPLE_TYPES = ['string', 'boolean', 'decimal', 'float', 'double',
                    'dateTime', 'time', 'date', 'base64Binary',
                    'normalizedString', 'integer', 'nonPositiveInteger',
                    'negativeInteger', 'long', 'int', 'short', 'byte',
                    'nonNegativeInteger', 'positiveInteger']


def getStringWithoutNamespace(originalString) -> str:
    namespaceSplit = originalString.split(':')
    return namespaceSplit[len(namespaceSplit) - 1].strip()
