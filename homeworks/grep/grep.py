import argparse
import sys
import re
import itertools
import copy


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
    for item in merged:
        array.append(all_lines[item])
    for item in array:
        output(item)


# Поиск по регулярке подходящих строк
def find_by_regexp(lines, params, reg_expr):
    i = 1
    for line in lines:
        if params.ignore_case is True:
            line = line.lower()
            reg_expr = reg_expr.lower()
            if re.search(reg_expr, line) is None:    # Если не совпадает с
                del(matched_lines[i])            # регуляркой то удаляем
            else:
                del(matched_lines_inverted[i])   # или оставляем для invert
        else:
            if re.search(reg_expr, line) is None:
                del(matched_lines[i])
            else:
                del(matched_lines_inverted[i])
        i += 1


def add_numbers(params):
    separator = ':'
    if params.line_number is True:     
        if params.context \
            or params.before_context \
                or params.after_context > 0:
            for item in all_lines:
                if all_lines[item] in matched_lines.values():
                    all_lines[item] = '{}{}{}'.format(str(item), separator, all_lines[item])
                else:
                    all_lines[item] = '{}-{}'.format(str(item), all_lines[item])
            for item in matched_lines:
                matched_lines[item] = '{}{}{}'.format(str(item), separator, matched_lines[item])
        else:               # Иначе всем элементам ставим : перед номером
            for item in all_lines:
                all_lines[item] =  \
                    str(item) + separator + all_lines[item]
            for item in matched_lines:
                matched_lines[item] = \
                    str(item) + separator + matched_lines[item]


def print_strings(params):
    before_context = 0
    after_context = 0
    if params.context > 0:                                            # C>0
        if params.after_context == 0 and params.before_context == 0:  # C>0
            before_context = params.context
            after_context = params.context
        elif params.after_context != 0 and params.before_context == 0:
            before_context = params.context                     # C>0,A>0
            after_context = params.after_context
        elif params.after_context == 0 and params.before_context != 0:
            before_context = params.before_context              # C>0,B>0
            after_context = params.context
        else:                                        # C>0,B>0,A>0 == b,a
            before_context = params.before_context
            after_context = params.after_context
        print_with_context(before_context, after_context, all_lines, matched_lines)
        return

    if params.context == 0:       # C=0
        if params.before_context > 0 or params.after_context > 0:
            before_context = params.before_context
            after_context = params.after_context
            print_with_context(before_context, after_context, all_lines, matched_lines)
            return
        for item in matched_lines:
            output(matched_lines[item])         # Вывод строк


def grep(lines, params):
    lines = [x.rstrip() for x in lines]            # Входные строки
    global matched_lines              # Строки прошедшие проверку
    global matched_lines_inverted     # Строки _НЕ_ прошедшие проверку
    global all_lines
    matched_lines = {}
    matched_lines_inverted = {}
    all_lines = {}

    reg_expr = params.pattern                       # Преобразование регулярки
    reg_expr = reg_expr.replace('?', '.')
    reg_expr = reg_expr.replace('*', '.*')

    for i, item in enumerate(lines, 1):
        all_lines[i] = item  # Заполняем словарь
    matched_lines_inverted = copy.deepcopy(all_lines)
    matched_lines = copy.deepcopy(all_lines)

    find_by_regexp(lines, params, reg_expr)

    if params.invert is True:            # Инверсия результатов если нужно
        matched_lines = matched_lines_inverted

    if params.count is True:      # Вывод только количества найденных строк
        output(str(len(matched_lines)))
        return

    add_numbers(params)
    print_strings(params)


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
