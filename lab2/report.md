# Лабораторная работа № 2

**Выполнила Трембач Антонина, M3301**

## Задача А. Анализ объектных файлов и компоновки

### Этап 0. Размеры файлов и секций

**1. **

```bash
size core.o legacy.o hotfix.o main.o
```

```text
   text    data     bss     dec     hex filename
    266    4040   50000   54306    d422 core.o
    172       0       4     176      b0 legacy.o
    127       0       0     127      7f hotfix.o
    118       0       0     118      76 main.o
```

Для сравнения с размерами файлов на диске выполнена команда:

```bash
ls -lh core.o legacy.o hotfix.o main.o
```

```text
-rw-rw-r-- 1 sol sol 6.1K Nov  5 20:49 core.o
-rw-rw-r-- 1 sol sol 1.5K Nov  5 20:49 hotfix.o
-rw-rw-r-- 1 sol sol 1.6K Nov  5 20:50 legacy.o
-rw-rw-r-- 1 sol sol 1.5K Nov  5 20:51 main.o
```

**2. Большой размер `bss` при небольшом размере файла:**

В файле `core.o` размер категории `bss` составляет 50 000 байт, хотя размер самого файла на диске - около 6,1 КБ. Это возможно, если модуль содержит большой объём неинициализированных или инициализированных нулём статических данных.

Секция `.bss` не хранит содержимое переменных на диске: в объектном файле задаются её размер и характеристики. При загрузке исполняемой программы для этой области предоставляется память, изначально заполненная нулями, поэтому увеличение `.bss` не требует хранения соответствующего количества нулевых байтов в объектном файле.

### Этап 1. Секции и строки

**3. Секция с данными только для чтения:**

Для сравнения таблиц секций выполнены команды:

```bash
readelf -SW core.o
readelf -SW legacy.o
readelf -SW hotfix.o
```

В `core.o` найдена секция `.rodata`, отсутствующая в `legacy.o` и `hotfix.o`. Она предназначена для данных только для чтения, в том числе строковых литералов. Соответствующая строка вывода:

```text
[ 5] .rodata PROGBITS 0000000000000000 001048 00004c 00 A 0 0 16
```

Размер секции `0x4c` равен 76 байтам. Для `.bss` в таблице указан тип `NOBITS`, подтверждающий отсутствие содержимого этой секции на диске, её размер в `core.o` равен `0xc350`, то есть 50 000 байт.

**4. Секретный токен:**

```bash
strings -a core.o
```

Вывод команды:

```text
System Initialized v1.0
FLAG{b1nary_4rch4eology_2026}
%s, Mode: %d
GCC: (Ubuntu 15.2.0-16ubuntu1) 15.2.0
core.c
large_buffer
internal_cleanup
system_mode
config_table
welcome_msg
secret_token
print_status
printf
.symtab
.strtab
.shstrtab
.rela.text
.data
.bss
.rodata
.rela.data.rel.local
.comment
.note.GNU-stack
.note.gnu.property
.rela.eh_frame
```

Найденный токен: `FLAG{b1nary_4rch4eology_2026}`.

### Этап 2. Таблицы символов

**5. Общие имена в нескольких модулях:**

```bash
nm core.o legacy.o hotfix.o main.o
```

Вывод команды:

```text
core.o:
0000000000000020 D config_table
0000000000000000 t internal_cleanup
0000000000000000 b large_buffer
                 U printf
0000000000000012 T print_status
0000000000000020 R secret_token
0000000000000000 D system_mode
0000000000000000 D welcome_msg

legacy.o:
000000000000001a T apply_legacy_patch
0000000000000000 b legacy_counter
0000000000000000 t legacy_helper
0000000000000004 C system_mode

hotfix.o:
0000000000000000 T apply_hotfix
0000000000000004 C system_mode

main.o:
                 U apply_hotfix
0000000000000000 T main
                 U print_status
```

В нескольких файлах встречаются имена `system_mode`, `apply_hotfix` и `print_status`.

| Имя | Файл | Тип `nm` | Значение |
|---|---|---|---|
| `system_mode` | `core.o` | `D` | Cимвол в секции `data`|
| `system_mode` | `legacy.o` | `C` | COMMON-символ |
| `system_mode` | `hotfix.o` | `C` | COMMON-символ |
| `apply_hotfix` | `hotfix.o` | `T` | Определение функции в области кода |
| `apply_hotfix` | `main.o` | `U` | Ссылка на функцию, определённую в другом модуле |
| `print_status` | `core.o` | `T` | Определение функции в области кода |
| `print_status` | `main.o` | `U` | Ссылка на функцию, определённую в другом модуле |

Пары определения `T` и ссылки `U` для функций являются обычной связью модулей. Символ `system_mode` надо рассмотреть подробнее - он представлен определением `D` в одном модуле и COMMON-символами в двух других.

**6. Типы и секции общих символов:**

```bash
readelf -sW core.o legacy.o hotfix.o main.o
```

Строки вывода для общих символов:

```text
File: core.o
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     7: 0000000000000000     4 OBJECT  GLOBAL DEFAULT    3 system_mode
    11: 0000000000000012    52 FUNC    GLOBAL DEFAULT    1 print_status

File: legacy.o
     6: 0000000000000004     4 OBJECT  GLOBAL DEFAULT  COM system_mode

File: hotfix.o
     3: 0000000000000001     4 OBJECT  GLOBAL DEFAULT  COM system_mode
     4: 0000000000000000    39 FUNC    GLOBAL DEFAULT    1 apply_hotfix

File: main.o
     4: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND print_status
     5: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND apply_hotfix
```

Индексы секций сопоставлены с таблицами `readelf -SW`:

| Имя | Файл | Тип `nm` | Размер, байт | `Ndx` | Секция или состояние |
|---|---|---|---|---|---|
| `system_mode` | `core.o` | `D` | 4 | 3 | `.data` |
| `system_mode` | `legacy.o` | `C` | 4 | `COM` | COMMON, ещё не размещён в обычной секции |
| `system_mode` | `hotfix.o` | `C` | 4 | `COM` | COMMON, ещё не размещён в обычной секции |
| `apply_hotfix` | `hotfix.o` | `T` | 39 | 1 | `.text` |
| `apply_hotfix` | `main.o` | `U` | 0 | `UND` | Не определён в этом файле |
| `print_status` | `core.o` | `T` | 52 | 1 | `.text` |
| `print_status` | `main.o` | `U` | 0 | `UND` | Не определён в этом файле |

Нулевой размер неопределённых символов в `main.o` не означает, что функции пустые: этот файл не содержит их определений и сведений об их размере.

Для COMMON-символов столбец `Value` в выводе `readelf` задаёт требуемое выравнивание: у `system_mode` в `legacy.o` оно равно 4 байтам, а в `hotfix.o` — 1 байту. Размер обоих объектов в столбце `Size` равен 4 байтам.

**7. Сопоставление объявлений `system_mode`:**

В уже известном исходном коде `hotfix.c` объявлен массив `char system_mode[4]`. Ему соответствует COMMON-символ размером 4 байта с выравниванием 1 байт.

В `core.o` символ `system_mode` является глобальным объектом размером 4 байта, определённым в `.data`. В `legacy.o` это COMMON-объект размером 4 байта с выравниванием 4 байта. Эти признаки согласуются с предположением, что в обоих модулях переменная объявлена как `int`, причём в `core.o` — с инициализатором. Также есть подсказка - строка формата `%s, Mode: %d` в `core.o`. Но таблица символов не содержит точного типа C: `OBJECT` не дает однозначно отличить `int` от массива или другого объекта такого же размера.

Потенциальный конфликт состоит в использовании одного имени для несовместимых типов. Компоновщик может объединить определения, после чего `apply_hotfix` запишет байты `'A'`, `'B'`, `'C'` и `'\0'` в ту же память, которую другой модуль может интерпретировать как целое число.

### Этап 3. Попытка компоновки

**8. Результат компоновки:**

```bash
gcc -fcommon core.o legacy.o hotfix.o main.o -o app
echo $?
```

Компоновщик не выдал ошибок или предупреждений, код завершения 0

Обычное определение `system_mode` из `core.o` имеет приоритет над COMMON-символами из `legacy.o` и `hotfix.o`. Размер всех трёх объектов одинаков и равен 4 байтам. Компоновщик разрешает символы по именам и не проверяет совместимость исходных типов C, поэтому возможное несоответствие `int` и `char[4]` не вызвало диагностики при данной команде.

Флаг `-fcommon` при передаче уже готовых объектных файлов не меняет находящиеся в них определения символов.

### Этап 4. Анализ исполняемого файла и исправление

**9. Размещение `system_mode` в исполняемом файле:**

```bash
nm app | rg system_mode
```

```text
0000000000004020 D system_mode
```

Буква `D` показывает, что символ находится в `.data`. Компоновщик выбрал обычное определение из `core.o`, которое имеет приоритет над COMMON-символами из `legacy.o` и `hotfix.o`.

**10. Запрет COMMON-символов и исправление `hotfix.c`:**

Сначала выполнена команда из условия:

```bash
gcc -fno-common main.o hotfix.o legacy.o core.o -o app_better
echo $?
```

Но она завершилась успешно. 

Ошибки не возникло, поскольку `-fno-common` влияет на компиляцию исходников, а не изменяет символы в уже готовых объектных файлах. Поэтому для воспроизведения конфликта создан файл `hotfix.c` с кодом из условия:

```c
char system_mode[4];

void apply_hotfix(void)
{
    system_mode[0] = 'A';
    system_mode[1] = 'B';
    system_mode[2] = 'C';
    system_mode[3] = '\0';
}
```

Повторив процесс

```bash
gcc -fno-common -c hotfix.c -o hotfix_no_common.o
nm hotfix_no_common.o
gcc main.o hotfix_no_common.o legacy.o core.o -o app_better
```

Получили:

```text
0000000000000000 T apply_hotfix
0000000000000000 B system_mode
/usr/bin/ld: warning: alignment 1 of normal symbol `system_mode' in hotfix_no_common.o is smaller than 4 used by the common definition in legacy.o
/usr/bin/ld: warning: NOTE: alignment discrepancies can cause real problems.  Investigation is advised.
/usr/bin/ld: core.o:(.data+0x0): multiple definition of `system_mode'; hotfix_no_common.o:(.bss+0x0): first defined here
collect2: error: ld returned 1 exit status
```

После пересборки `system_mode` стал обычным глобальным определением в `.bss` (тип `B`), которое конфликтует с определением того же имени в `.data` файла `core.o`. Дополнительно компоновщик сообщил о различии выравнивания: 1 байт у массива в `hotfix_no_common.o` и 4 байта у COMMON-символа в `legacy.o`.

Для устранения конфликта без изменения имени переменной её объявление в `hotfix.c` изменено:

```c
static char system_mode[4];
```

Спецификатор `static` задаёт внутреннее связывание: переменная становится отдельным объектом, доступным по имени только внутри этого файла.

Запускаем исправленное:

```bash
gcc -fno-common -c hotfix.c -o hotfix_static.o
nm hotfix_static.o
gcc main.o hotfix_static.o legacy.o core.o -o app_fixed
echo $?
```

Вывод:

```text
0000000000000000 T apply_hotfix
0000000000000000 b system_mode
0
```

Строчная `b` подтверждает, что `system_mode` стал локальным символом в `.bss`. Компоновка прошла успешно с кодом 0, без прежнего конфликта определений.

Это исправление обеспечивает успешную сборку, но меняет связь данных между модулями: `apply_hotfix` записывает символы в собственный массив и больше не изменяет глобальный `system_mode` из `core.o`. Если патч должен менять именно общую переменную, необходимо согласовать её тип и назначение между модулями и использовать корректное объявление `extern`.

