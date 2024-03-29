import logging

NULL_DESCRIPTION_MESSAGE = 'Отсутствует описание (аннотация) элемента'
POSSIBLE_KEY_VALUE_MESSAGE = 'Возможная структура key-value'
POSSIBLE_CARD_NUMBER_MESSAGE = 'Возможный элемент с номером карты'
ARRAY_EXCESS_MAX_ITEMS_MESSAGE = 'Указанное максимальное количество ' \
                                 'элементов массива превышает допустимое' \
                                 ', требуется согласование УЭК'
STRING_NO_MAX_LENGTH_MESSAGE = 'Отсутствует ограничение по длине строки'
STRING_NO_PATTERN_MESSAGE = 'Отсутствует паттерн для строки'
STRING_EXCESS_MAX_LENGTH_MESSAGE = 'Указанная максимальная длина ' \
                                   'строки выше допустимой' \
                                   ', требуется согласование УЭК'
NUMERIC_NO_MIN_VALUE_MESSAGE = 'Не указано минимальное значение для числа'
NUMERIC_NO_MAX_VALUE_MESSAGE = 'Не указано максимальное значение для числа'
NUMERIC_EXCESS_MIN_VALUE_MESSAGE = 'Указанное минимальное значение ' \
                                   'для числа меньше допустимого'
NUMERIC_EXCESS_MAX_VALUE_MESSAGE = 'Указанное максимальное значение ' \
                                   'для числа больше допустимого'


FILE_PROCESS_START_TEXT = ['Выполняется обработка файла, ожидайте!',
                           'По окончании вы сможете запустить валидацию.']
FILE_PROCESS_FINISH_TEXT = ['Обработка файла закончена!',
                            'Выберите элементы из выпадающего списка.',
                            'Затем нажмите кнопку "Валидировать схему".']

LOGGER_FORMAT = "%(asctime)s - [%(levelname)s] - (%(filename)s:%(" \
                "funcName)s:%(lineno)d) - %(message)s"
LOGGER_FILE_NAME = "validatorLog.log"


class ColoredFormatter(logging.Formatter):
    # FORMAT = "%(asctime)s - [%(levelname)s] - %(message)s (%(filename)s:%(
    # funcName)s:%(lineno)d)"
    # FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(
    # filename)s:%(lineno)d)"
    # FORMAT = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(
    # lineno)d - %(message)s"

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


def getElementSiblings(elemObject, objectsDict) -> dict:
    resultDict = {}

    if hasattr(elemObject, 'fullPath'):
        if (len(parentPath := elemObject.fullPath.rpartition('/')[0]) > 0):
            for otherObjectKey, otherObject in objectsDict.items():
                if otherObject != elemObject \
                        and hasattr(otherObject, 'fullPath') \
                        and otherObject.fullPath.rpartition('/')[0] == parentPath:
                    resultDict[otherObjectKey] = otherObject

    return resultDict
