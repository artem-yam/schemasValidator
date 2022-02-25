# schemasValidator

- НЕ ОБЯЗАТЕЛЬНО, НО БУДЕТ КРУТО
    - менять список тегов для выбора после ручного редактирования схемы с левом поле
        (мб по событию потери фокуса на поле: 
            def focusOut(...):
                if textBefore!=textAfter:
                    снова парсим схему    
        ) 
    - копирование в файл
    - выделение/копирование только красных ошибок
        -   выделение всех/красных/желтых
        -   копирование всех/красных/желтых в буфер/файл 
    - ручное изменение типа сообщения (с инфо на ошибку и наоборот) ?
    - при выборе сообщения  выделять связанный тег в схеме слева


TODO общее:
    -+   отображать имя активной схемы
    -+   на строки и массивы - макс ограничение длины поменять на 4096


TODO json:
    -+   если есть patternProperties, то доп. проверка наличия maxProperties
    -+   если есть additionalProperties и не равно false,
        то доп. проверка наличия maxProperties
    -+   проверка наличия additionalProperties:false только для object 
    -+   для массива при пустом items не должно быть проверок
        на ограниченность массива, additionalItems, additionalProperties
    -   проверить $ref
    -   объединять элементы и типы 
    -   сделать ошибку при циклических ссылках
    -   переделать поиск key-value pair
    (искать комбинацию key|param + value)  


TODO xsd:
-   полное отсутствие типа у элемента +++ 
    (пример: /GetStatementCVDataRqType/Any в тестовой схеме 3)
-   парсинг:
    -+?   объединять элементы и типы
        -   ref +++
        -   парсить всю цепочку из simpleType +++
    -+?   choice  и т.п. на уровне с element 
        (пример: контейнер GetDebtInfoForClassificationRsType 
        в GetDebtInfoForClassification_151121.xsd)
    -   цикличные ссылки
        (пример:    1)  recreateObjects.folder... 
                    2)  /ticket/permissions/allow...
                        /ticket/permissions/deny...
                                                        в ecm_mq_3.10.xsd)
    !!!-   complexContent внутри complexType работает некорректно
         (пример:   1)  permission... 
                    2)  findData...
                                                        в ecm_mq_3.10.xsd)  
    -+?   аттрибуты
        (пример: folderSpecWithFailureError в ecm_mq_3.10.xsd)
        (пример: val_date и т.п. в GetDebtInfoForClassification_151121.xsd)
        (проверки аналогичны для строк и чисел)
-   сделать ошибку при циклических ссылках
-   переделать поиск key-value pair     ??? пока под вопросом
    (искать комбинацию key|param + value)

Сделано для xsd:
-   реализовать выбор элементов для валидации
-   копирование результатов 
-   парсинг:
    -   добавил в объекты поле "tag" для учета разных тегов с одинаковыми названиями 
    -   парсить все attrib в поля объекта +++
    -   fullPath +++
    -   отрезать неймспейс у типов +++
-   проверки
    -   ограничение массива
    -   элемент с номером карты   (инфо)
    -   наличие annotation (инфо)   +++
    -   any  - <xsd:element name="SPName" type="xsd:anyType">   +++
    -   наличие паттернов у строк   (инфо)  +++
    -   ограничение длины строк (length, maxLength) +++
    -   для строк проверка длины через паттерн 
        (сделал только проверку отсутствия '+' и '*')    +++
    -   проверять элементы без типа
    -   ограничение чисел (minExclusive, minInclusive, maxExclusive, maxInclusive, totalDigits) ???
-   конфигуратор:
    -   ограничение массива
    -   макс длина строки
    -   макс размер числа
    -   мин размер числа
    -   xs:any
    
+++Сделано для json:
-   гибкий UI
-   объекты с динамическим набором полей
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
    -   элемент с номером карты   (инфо)
    -   наличие паттернов у строк   (инфо)
    -   массивы
        -   наличие описания items
        -   ограничение размера массивов
        -   additionalItems: false и uniqueItems: true
    -   ограничение чисел (minimum, exclusiveMinimum, maximum, exclusiveMaximum)
    -   additionalProperties:false для элементов с детьми
    -   any ???
    -   для строк проверка длины через паттерн
        (сделал только проверку отсутствия '+' и '*') ???
-   конфигуратор:
    -   макс длина строки
    -   макс длина массива
    -   макс размер числа
    -   мин размер числа
    -   указание типа
-   вывод сообщений по проверкам