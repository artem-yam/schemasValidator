# schemasValidator

TODO:
-   UI
    -   по макету Жени
-   конфигуратор:   ???
-   добавить проверки на json схемы:    ???
 
 any в xsd - <xsd:element name="SPName" type="xsd:anyType">   

    
Сделано:
-   гибкий UI
-   объекты с динимическим набором полей
-   чтение json из файла
-   drag'n'drop json файла
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
-   конфигуратор:
    -   макс длина строки
    -   макс длина массива
    -   макс размер числа
    -   мин размер числа
    -   указание типа    
-   вывод сообщений по проверкам