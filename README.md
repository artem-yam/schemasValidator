# schemasValidator

TODO:
-   UI
    -   сделать гибкий UI, 
        размеры элементов меняются от размера окна приложения
    -   по макету Жени
-   конфигуратор
-   добавить проверки на json схемы:
    -   для строк проверка длины через паттерн ???
 
 
 any в xsd - <xsd:element name="SPName" type="xsd:anyType">   

    
Сделано:
-   мой начальный макет UI
-   объекты с динимическим набором полей
-   чтение json из файла
-   парсинг json текста в объекты
    -   при парсинге учитываются блоки properties и definitions
    -   парсинг items в массивах
    -   парсинг oneOf
-   реализованы проверки
    -   наличие description (инфо)
    -   ограничение длины строк
    -   версия драфта   (инфо)
    -   наличие паттернов у строк   (инфо)
    -   массивы
        -   наличие описания items
        -   ограничение размера массивов
        -   additionalItems: false и uniqueItems: true
    -   ограничение чисел (minimum, exclusiveMinimum, maximum, exclusiveMaximum)
    -   additionalProperties:false для элементов с детьми
    -   any ???
    -   для строк проверка длины через паттерн
        (сделал только провеку отсутствия '+' и '*') ???
-   вывод сообщений по проверкам