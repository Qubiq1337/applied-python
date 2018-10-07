import argparse
import sys
import re
import itertools


def output(line):
    print(line)


def print_with_context(before, after, all_lines, passed):
    all_lines_keys = list(all_lines.keys())
    passed_keys = list(passed.keys())
    array = []
    x = 0
    y = 0
    for i, _ in enumerate(passed_keys):
        if passed_keys[i] - before - 1 < 0:
            x = 0
        else:
            x = passed_keys[i] - before - 1
        y = passed_keys[i] + after
        array.append(all_lines_keys[x:y])
    merged = list(set(itertools.chain(*array)))
    array = []
    for _, item in enumerate(merged):
        array.append(all_lines[item])
    for _, item in enumerate(array):
        output(item)


def grep(lines, params):
    lines = [x.strip() for x in lines]            # Входные строки
    passed_lines = {}                             # Строки прошедшие проверку
    passed_lines_inverted = {}               # Строки _НЕ_ прошедшие проверку
    all_lines = {}
    reg_expr = params.pattern                       # Преобразование регулярки
    reg_expr = reg_expr.replace('?', '.')
    reg_expr = reg_expr.replace('*', '.*')
    for i, item in enumerate(lines, 1):
        passed_lines[i] = item
        passed_lines_inverted[i] = item           # Заполняем словарь
        all_lines[i] = item                  # Сохраняем все строки для context

    i = 1
    for line in lines:                    # Поиск по регулярке подходящих строк
        if params.ignore_case is True:    
            line = line.lower()
            reg_expr = reg_expr.lower()
            if re.search(reg_expr, line) is None:    # Если не совпадает с регуляркой то удаляем или оставляем для ключа invert
                del(passed_lines[i])
            else:
                del(passed_lines_inverted[i])
        else:
            if re.search(reg_expr, line) is None:
                del(passed_lines[i])
            else:
                del(passed_lines_inverted[i])
        i += 1

    if params.invert is True:                     # Инверсия результатов если нужно
        passed_lines = passed_lines_inverted

    separator = ':'
    before_context = 0
    after_context = 0

    if params.count is True:                      # Вывод только количества найденных строк
        output(str(len(passed_lines)))
    else:
        if params.line_number is True:            # Если требуется добавляем номера строк перед строкой
            if params.context \
                or params.before_context \
                    or params.after_context > 0:                                           # Если есть context то меняем логику
                for _, item in enumerate(all_lines):
                    if all_lines[item] in passed_lines.values():
                        all_lines[item] = str(item) + ':' + all_lines[item]
                    else:
                        all_lines[item] = str(item) + '-' + all_lines[item]
                for _, item in enumerate(passed_lines):
                    passed_lines[item] =  \
                        str(item) + separator + passed_lines[item]
            else:               # Иначе всем элементам ставим : перед номером
                for _, item in enumerate(all_lines):
                    all_lines[item] =  \
                        str(item) + separator + all_lines[item]
                for _, item in enumerate(passed_lines):
                    passed_lines[item] = \
                        str(item) + separator + passed_lines[item]

        if params.context > 0:                                            # C>0
            if params.after_context == 0 and params.before_context == 0:  # C>0
                before_context = params.context
                after_context = params.context
            elif params.after_context != 0 and params.before_context == 0:   # C>0,A>0
                before_context = params.context
                after_context = params.after_context
            elif params.after_context == 0 and params.before_context != 0:   # C>0,B>0
                before_context = params.before_context
                after_context = params.context
            else:                                        # C>0,B>0,A>0 == b,a
                before_context = params.before_context
                after_context = params.after_context
            print_with_context(before_context, after_context, all_lines, passed_lines)

        elif params.context == 0:
            if params.before_context > 0 or params.after_context > 0:       # C=0
                before_context = params.before_context
                after_context = params.after_context
                print_with_context(before_context, after_context, all_lines, passed_lines)
            else:
                for _, item in enumerate(passed_lines):
                    output(passed_lines[item])           # Вывод строк


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
