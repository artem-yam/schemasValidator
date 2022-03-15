# schemasValidator

НЕ ОБЯЗАТЕЛЬНО, НО БУДЕТ КРУТО:
- менять список тегов для выбора после ручного редактирования схемы с левом поле
  (мб по событию потери фокуса на поле:
  def focusOut(...):
  if textBefore!=textAfter:
  снова парсим схему    
  )
- копирование в файл
- выделение/копирование только красных ошибок
- выделение всех/красных/желтых
- копирование всех/красных/желтых в буфер/файл
- ручное изменение типа сообщения (с инфо на ошибку и наоборот) ?
- при выборе сообщения выделять связанный тег в схеме слева


TODO общее:
- ОПТИМИЗАЦИЯ: !!!
  Элементы для выбора брать из текста схемы, затем парсить только выбранные элементы+все типы
- логирование в файл !!!


TODO json:
- под вопросом (уточняется):
  -??? парсинг patternProperties ??? -??? в patternProperties проверять ограничение имени свойства по длине
- сделать ошибку при циклических ссылках
- переделать поиск key-value pair
  (искать комбинацию key|param + value)


TODO xsd:
- переделать extension и restriction
  (пример: /ticket/permissions/allow/attrs)
- понять, почему в путях остаются неймспейсы ++?
- полное отсутствие типа у элемента +++
  (пример: /GetStatementCVDataRqType/Any в тестовой схеме 3)
- парсинг:
    - ref +++
    - цикличные ссылки
      (пример:    1)  recreateObjects.folder... 2)  /ticket/permissions/allow... /ticket/permissions/deny... в
      ecm_mq_3.10.xsd)
    - complexContent внутри complexType работает некорректно                !!!
      (пример:   1)  permission... 2)  findData... в ecm_mq_3.10.xsd)
- сделать ошибку при циклических ссылках
- переделать поиск key-value pair ??? пока под вопросом
  (искать комбинацию key|param + value)


Сделано общее:
- гибкий UI
- объекты с динамическим набором полей
- чтение из файла
- drag'n'drop файла
- вывод сообщений по проверкам
- реализовать выбор элементов для валидации
- копирование результатов
- отображать имя активной схемы


Сделано для xsd:
- парсинг:
    - добавил в объекты поле "tag" для учета разных тегов с одинаковыми названиями
    - парсить все attrib в поля объекта +++
    - fullPath +++
    - отрезать неймспейсы +++
    - все attribute как элементы
    - объединение элементов с их типами:
      - Если тип - simpleType, то в этом типе ищется по цепочке до простого типа
      - Если тип - complexType, то копируется объекты типа и всех подтипов 
      и на них переносится полный путь от элемента, 
      на сам тип также переносятся доп. свойства элемента 
- проверки:
    - ограничение массива
    - элемент с номером карты   (инфо)
    - наличие annotation (инфо)   +++
    - any - <xsd:element name="SPName" type="xsd:anyType">   +++
    - наличие паттернов у строк   (инфо)  +++
    - ограничение длины строк (length, maxLength) +++
    - для строк проверка длины через паттерн
      (сделал только проверку отсутствия '+' и '*')    +++
    - проверять элементы без типа
    - ограничение чисел (minExclusive, minInclusive, maxExclusive, maxInclusive, totalDigits) ???
- конфигуратор:
    - ограничение массива
    - макс длина строки
    - макс размер числа
    - мин размер числа
    - xs:any
    - на строки и массивы - макс ограничение длины поменять на ~~4096~~255


Сделано для json:
- парсинг:
    - при парсинге учитываются блоки properties и definitions
    - парсинг items в массивах
    - парсинг oneOf
    - объединять элементы и типы через $ref
- проверки:
    - наличие description (инфо)
    - ограничение длины строк
    - версия драфта   (инфо)
    - элемент с номером карты   (инфо)
    - наличие паттернов у строк   (инфо)
    - массивы
        - наличие описания items
        - ограничение размера массивов
        - additionalItems: false и uniqueItems: true
    - ограничение чисел (minimum, exclusiveMinimum, maximum, exclusiveMaximum)
    - additionalProperties:false для элементов с детьми
    - any
    - для строк проверка длины через паттерн
      (сделал только проверку отсутствия '+' и '*')
    - для массива при пустом items не должно быть проверок на ограниченность массива, additionalItems,
      additionalProperties
    - если есть patternProperties, то доп. проверка наличия maxProperties
    - проверка наличия additionalProperties:false только для object
    - если есть additionalProperties и не равно false, то доп. проверка наличия maxProperties
    - убрать проверку наличия maxProperties при patternProperties=true
- конфигуратор:
    - макс длина строки
    - макс длина массива
    - макс размер числа
    - мин размер числа
    - указание типа
    - на строки и массивы - макс ограничение длины поменять на ~~4096~~255