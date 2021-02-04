import psycopg2
import os
from pprint import pprint


def find_sql_files(path):
    result = []
    for root, directory, file in os.walk(path):
        for f in file:
            if f[-4:] == '.sql':
                result.append(root + '\\' + f)
    return result


def read_file(path_sql):
    with open(path_sql) as file:
        sql_script = file.read()
    return sql_script


def split_sql(sql_script):
    flg_text = False
    i = 0
    j = 0
    result = []
    while i < len(sql_script):
        if sql_script[i] == "'":
            flg_text = not flg_text
        if sql_script[i] == ';' and not flg_text:
            result.append(sql_script[j:i + 1])
            j = i + 1
        i += 1
    if len(sql_script) != 0 and sql_script[-1] != ';' and not flg_text:
        result.append(sql_script[j:i + 1].strip())
    return result


def delete_comment(commands):
    line_comment = False
    multiline_comment = False
    flg_text = False
    i = 0
    j = 0
    while i < len(commands):
        if commands[i:i+2] == '--' and not multiline_comment and not flg_text:
            j = i
            line_comment = True
        if commands[i] == '\n' and line_comment:
            commands = commands[:j]+commands[i+1:]
            line_comment = False
            i = j
        if commands[i:i+2] == '/*' and not line_comment and not flg_text:
            j = i
            multiline_comment = True
        if commands[i:i+2] == '*/' and multiline_comment:
            commands = commands[:j]+commands[i+2:]
            multiline_comment = False
            i = j
        if commands[i] == "'" and not line_comment and not multiline_comment:
            flg_text = not flg_text
        i += 1
    if commands[-1] != '\n' and line_comment and not multiline_comment and not flg_text:
        commands = commands[:j]+commands[i:]
    return commands


def validate_syntax(sql_command):
    try:
        connection = psycopg2.connect(database="demo", user="annaum", password="123", host="192.168.1.67", port="5432")
        cursor = connection.cursor()
        a = """DO $SYNTAX_CHECK$ BEGIN RETURN; {query} END; $SYNTAX_CHECK$;""".format(query=sql_command)
        cursor.execute(a)
        cursor.close()
        connection.close()
    except psycopg2.errors.SyntaxError as e:
        return str(e)


def validate_package(path):
    result = {}
    for path_sql in find_sql_files(path):
        syntax_error = []
        script_file = read_file(path_sql)
        if len(script_file) != 0:
            clean_commands = delete_comment(script_file)
            for sql_command in split_sql(clean_commands):
                if validate_syntax(sql_command) is not None:
                    syntax_error.append(validate_syntax(sql_command))
            result[path_sql] = syntax_error
        else:
            result[path_sql] = ["This file is empty!!!" + '\n']
    return result


def error_format(files_and_errors):
    result = []
    y = 1
    while y == True:
        for i in files_and_errors:
            result.append(i + '\n')
            for x in files_and_errors[i]:
                result.append(str(y) + ')')
                y += 1
                result.append(x)
            result.append('-'*50 + '\n')
    return result


if __name__ == '__main__':
    path_dir = 'D:/Project/test'
    with open(path_dir + '/error.txt', 'w') as new_file:
        new_file.flush()

    result_validate = validate_package(path_dir)
    result_txt = error_format(result_validate)

    with open(path_dir + '/error.txt', 'w') as f:
        f.write(' '.join(result_txt))
