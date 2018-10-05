
import argparse
import sys
import re


def output(line):
    print(line)


def grep(lines, params):

    regexp = params.pattern                       #Преобразование регулярки для использования пакета re
    regexp = regexp.replace('?','.')
    regexp = regexp.replace('*','.*')

    lines = [x.strip() for x in lines]            #Входные строки
    passed_lines = {}                             #Строки прошедшие проверку
    passed_lines_inverted = {}                    #Строки _НЕ_ прошедшие проверку
    all_lines = {}
    for i,item in enumerate(lines,1):
        passed_lines[i] = item
        passed_lines_inverted[i] = item           #Заполняем словарь - ключ это номер строки с 1, значение это сама строка.
        all_lines[i] = item                       #Сохраняем все строки для context

    i = 1
    for line in lines:                            #Поиск по регулярке подходящих строк
        if params.ignore_case == True:            #Проверка на независимость от регистра
            line = line.lower()
            regexp = regexp.lower()
            if re.search(regexp,line) is None:    #Если не совпадает с регуляркой то удаляем или оставляем для ключа invert
                del(passed_lines[i])
            else:
                del(passed_lines_inverted[i])
        else:
            if re.search(regexp,line) is None:
                del(passed_lines[i])
            else:
                del(passed_lines_inverted[i])
        i += 1

    if params.invert == True:                     #Инверсия результатов если нужно
        passed_lines = passed_lines_inverted

    separator = ':'
    before_context = 0
    after_context = 0

    if params.count == True:                      #Вывод только количества найденных строк
        output(str(len(passed_lines)))
    else:
           
        if params.line_number == True:            #Если требуется добавляем номера строк перед строкой
            if params.context \
            or params.before_context \
            or params.after_context > 0:                                           #Если есть context то меняем логику
                for _,item in enumerate(all_lines):
                    all_lines[item] =  \
                    str(item) + '-' + all_lines[item]
                for _,item in enumerate(passed_lines):
                    passed_lines[item] =  \
                    str(item) + separator + passed_lines[item]               
            else:                                                                   #Иначе всем элементам ставим : перед номером 
                for _,item in enumerate(all_lines):
                    all_lines[item] =  \
                    str(item) + separator + all_lines[item]
                for _,item in enumerate(passed_lines):
                    passed_lines[item] = \
                    str(item) + separator + passed_lines[item]

        if params.context > 0:                                                              #C>0
            if params.after_context == 0 and params.before_context == 0:                    #C>0
                before_context = params.context
                after_context = params.context 
            elif params.after_context != 0 and params.before_context == 0:                   #C>0,A>0
                before_context = params.context
                after_context = params.after_context
            elif params.after_context == 0 and params.before_context != 0:                   #C>0,B>0
                before_context = params.before_context
                after_context = params.context  
            else:                                                                            #C>0,B>0,A>0 == b,a
                before_context = params.before_context
                after_context = params.after_context
                print(before_context,after_context)                        
        elif params.context == 0:                                                           #C=0
            before_context = params.before_context
            after_context = params.after_context            
            print(before_context,after_context,passed_lines,passed_lines_inverted,all_lines)  
        else:
            for _,item in enumerate(passed_lines):
                output(passed_lines[item])           #Вывод строк
    for _,item in enumerate(passed_lines):
        output(passed_lines[item])           #Вывод строк
    #output(passed_lines)
    #output(all_lines)
    #array_of_magic_numbers = [x for x in all_lines.keys]
    #output(array_of_magic_numbers)



#------------------------------------------------------------------
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
