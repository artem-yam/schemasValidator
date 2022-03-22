import logging


def getStringWithoutNamespace(originalString) -> str:
    namespaceSplit = originalString.split(':')
    return namespaceSplit[len(namespaceSplit) - 1].strip()


XSD_SIMPLE_TYPES = ['string', 'boolean', 'decimal', 'float', 'double',
                    'dateTime', 'time', 'date', 'base64Binary',
                    'normalizedString', 'integer', 'nonPositiveInteger',
                    'negativeInteger', 'long', 'int', 'short', 'byte',
                    'nonNegativeInteger', 'positiveInteger']

LOGGER_FORMAT = "%(asctime)s - [%(levelname)s] - (%(filename)s:%(funcName)s:%(lineno)d) - %(message)s"
LOGGER_FILE_NAME = "validatorLog.log"


class ColoredFormatter(logging.Formatter):
    # FORMAT = "%(asctime)s - [%(levelname)s] - %(message)s (%(filename)s:%(funcName)s:%(lineno)d)"
    # FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    # FORMAT = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[20;%dm"
    # BOLD_COLOR_SEQ = "\033[1;%dm"

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GREY, WHITE = range(9)

    COLORS = {
        'WARNING': YELLOW,
        'INFO': WHITE,
        'DEBUG': GREY,
        'CRITICAL': YELLOW,
        'ERROR': RED
    }

    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        color_format = self.COLOR_SEQ % (
                30 + self.COLORS[levelname]) + self._fmt + self.RESET_SEQ
        return logging.Formatter(color_format).format(record)

        # if levelname in self.COLORS:
        #     levelname_color = self.COLOR_SEQ % (
        #             30 + self.COLORS[levelname]) + levelname + self.RESET_SEQ
        #     record.levelname = levelname_color
        # return logging.Formatter.format(self, record)


sh = logging.StreamHandler()
sh.setFormatter(ColoredFormatter(LOGGER_FORMAT))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=(logging.FileHandler(LOGGER_FILE_NAME, 'w'), sh),
    format=LOGGER_FORMAT
)
