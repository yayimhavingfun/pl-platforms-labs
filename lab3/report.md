# Лабораторная работа № 3

**Выполнила Трембач Антонина, M3301**

## Задача А. Как пройти в библиотеку?

### Этап 1. Статическая библиотека

```bash
gcc -c vector_math.c -o vector_math.o
ar rcs libmath_static.a vector_math.o
g++ -c main.cpp -o main.o
g++ main.o -L. -lmath_static -o app_static
./app_static
```

Вывод программы:

```text
Library version: v2.4.1-release
Dot product result: 32
```

Результат соответствует вычислению `1 × 4 + 2 × 5 + 3 × 6 = 32`.

**1. Флаги `ar rcs`**

- `r` добавляет файл в архив или заменяет одноимённый элемент.
- `c` подавляет сообщение о создании архива, если его ещё нет.
- `s` создаёт или обновляет индекс символов для компоновщика.

При повторном запуске той же команды объектный файл `vector_math.o` заменяется в архиве, а индекс символов обновляется.

**2. Символы в `main.o`**

```bash
nm main.o
```

```text
                 U dot_product
                 U get_lib_version
                 U _GLOBAL_OFFSET_TABLE_
0000000000000000 T main
                 U __stack_chk_fail
                 U _ZNSolsEi
                 U _ZNSolsEPFRSoS_E
0000000000000027 r _ZNSt8__detail30__integer_to_chars_is_unsignedIjEE
0000000000000028 r _ZNSt8__detail30__integer_to_chars_is_unsignedImEE
0000000000000029 r _ZNSt8__detail30__integer_to_chars_is_unsignedIyEE
                 U _ZSt21ios_base_library_initv
                 U _ZSt4cout
                 U _ZSt4endlIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_
                 U _ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc
```

Буква `T` у `main` показывает, что функция определена в секции кода. Для глобальной функции `main` компилятор сохраняет имя символа без кодирования, чтобы стартовый код мог вызвать её по имени `main`.

Имена `dot_product` и `get_lib_version` сохранены благодаря объявлениям с `extern "C"` в заголовке, буква `U` означает, что `main.o` содержит ссылки на эти функции, при компоновке их определения берутся из `libmath_static.a`.

### Этап 2. Динамическая библиотека

```bash
gcc -c vector_math.c -o vector_math_nopic.o
gcc -shared -o libmath_broken.so vector_math_nopic.o
echo $?
```

Получили код завершения `0`. В этой сборке ссылки в объектном файле удалось обработать при создании `.so`, поэтому ожидаемая по условию ошибка не возникла, для явного получения позиционно-независимого кода использован флаг `-fPIC`.

```bash
gcc -c -fPIC vector_math.c -o vector_math_pic.o
gcc -shared -o libmath_dynamic.so vector_math_pic.o
g++ main.o -L. -lmath_dynamic -o app_dynamic
LD_LIBRARY_PATH="$PWD" ./app_dynamic
size app_static app_dynamic
```

```text
Library version: v2.4.1-release
Dot product result: 32
   text    data     bss     dec     hex filename
   2548     656     280    3484     d9c app_static
   2517     680     280    3477     d95 app_dynamic
```

Столбец `text` уменьшился на 31 байт. В статическом варианте код функций библиотеки входит в исполняемый файл, в динамическом варианте он остаётся в `libmath_dynamic.so`, которую загрузчик подключает при запуске. 

### Этап 3. Порядок компоновки

Сначала указала библиотеку перед `main.o`.

```bash
g++ -L. -lmath_dynamic main.o -o app_wrong_order
echo $?
```

```text
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x63): undefined reference to `get_lib_version'
/usr/bin/ld: main.cpp:(.text+0xb4): undefined reference to `dot_product'
collect2: error: ld returned 1 exit status
1
```

Затем указала `main.o` перед библиотекой.

```bash
g++ main.o -L. -lmath_dynamic -o app_correct
echo $?
```

Вторая команда компоновки завершилась с кодом `0`.

Компоновщик читает аргументы слева направо. В `U` находятся неразрешённые ссылки, в `D` - известные определения, в `E` - включённые файлы. Для `.so` включение означает, что программа сохраняет зависимость от библиотеки.

В первой попытке компоновщик встретил библиотеку до `main.o`. В этот момент в `U` ещё не было ссылок на `get_lib_version` и `dot_product`, и библиотека не попала в `E`. После обработки `main.o` определение `main` попало в `D`, а ссылки на обе функции - в `U`. Они остались неразрешёнными, поэтому компоновщик выдал `undefined reference`.

Когда `main.o` стоит первым, обе ссылки уже в `U` к моменту обработки библиотеки. Компоновщик сохраняет зависимость в `E`, добавляет определения функций в `D` и убирает ссылки из `U`.

### Этап 4. Кодирование имён и `extern "C"`

Временно убрала обёртку `extern "C"` из `vector_math.h`. Пересобрала `main.cpp`, сравнила символы и попробовала скомпоновать программу.

```bash
g++ -c main.cpp -o main_no_extern.o
nm main_no_extern.o | rg 'dot_product|get_lib_version'
nm -D libmath_dynamic.so | rg 'dot_product|get_lib_version'
g++ main_no_extern.o -L. -lmath_dynamic -o app_no_extern
```

```text
                 U _Z11dot_productPKiS0_i
                 U _Z15get_lib_versionv
000000000000110a T dot_product
00000000000010f9 T get_lib_version
/usr/bin/ld: main_no_extern.o: in function `main':
main.cpp:(.text+0x63): undefined reference to `get_lib_version()'
/usr/bin/ld: main.cpp:(.text+0xb4): undefined reference to `dot_product(int const*, int const*, int)'
collect2: error: ld returned 1 exit status
```

В `main_no_extern.o` функции получили имена `_Z11dot_productPKiS0_i` и `_Z15get_lib_versionv`. Библиотека экспортирует их как `dot_product` и `get_lib_version`. Без `extern "C"` компилятор C++ применил name mangling. Имена символов разошлись, поэтому компоновщик выдал `undefined reference` для обеих функций.

Вернула `extern "C"` в заголовок, пересобрала и запустила программу.

```bash
g++ -c main.cpp -o main.o
g++ main.o -L. -lmath_dynamic -o app_correct
LD_LIBRARY_PATH="$PWD" ./app_correct
```

```text
Library version: v2.4.1-release
Dot product result: 32
```
