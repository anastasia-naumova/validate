import os
import re


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
            result.append(sql_script[j:i + 1].strip())
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


def data_conversion(all_path_script):
    count_com = 1
    i = 0
    all_commands = []
    for path in all_path_script:
        for command in all_path_script[path]:
            a = 0
            b = 1
            while a < len(command):
                if command[a:b + 1] == '  ':
                    command = re.sub(r'\s+', ' ', command)
                a += 1
                b += 1
            name_object = re.search(r'\S+\.\S+[^;]', command)
            j = name_object.start()
            one_command = {}
            one_command['number_command'] = count_com
            one_command['path_sql'] = path
            one_command['name_object'] = name_object.group(0).strip().lower()
            one_command['name_command'] = command[i:j].strip().lower()
            count_com += 1
            all_commands.append(one_command)
    return all_commands


def group_objects(commands):
    result = {}
    for command in commands:
        if command['name_object'] in result:
            result[command['name_object']].append(command)
        else:
            result[command['name_object']] = [command]
    return result


def validate_create_command(groups_objects):
    result = {}
    for obj in groups_objects:
        create_number = 0
        drop_number = 0
        for i in groups_objects[obj]:
            if 'create table' in i['name_command']:
                create_number = i['number_command']
            if 'drop table' in i['name_command']:
                drop_number = i['number_command']
        if drop_number == 0 and create_number != 0:
            if i['path_sql'] not in result:
                result[i['path_sql']] = [i]
            else:
                result[i['path_sql']].append(i)
    return result


def validate_commands(path):
    all_path_script = {}
    for path_sql in find_sql_files(path):
        script_file = read_file(path_sql)
        if len(script_file) != 0:
            clean_commands = delete_comment(script_file)
            all_path_script[path_sql] = split_sql(clean_commands)
    all_commands = data_conversion(all_path_script)
    groups_objects = group_objects(all_commands)
    create_commands = validate_create_command(groups_objects)
    return create_commands


def error_format(create_commands):
    result = []
    y = 1
    while y == True:
        for i in create_commands:
            result.append(i + '\n')
            for x in create_commands[i]:
                result.append(str(y) + ')')
                y += 1
                result.append('Есть комманда: ' + x['name_command'].upper() + '.\n')
                result.append('Необходимо добавить комманду:' + 'DROP TABLE ' + x['name_object'] + '.' + '\n'*2)
            result.append('-'*50 + '\n')
    return result


if __name__ == '__main__':
    path_dir = 'D:/Project/test'
    with open(path_dir + '/error.txt', 'w') as new_file:
        new_file.flush()

    inv_command = validate_commands(path_dir)
    result = error_format(inv_command)

    with open(path_dir + '/error.txt', 'w', encoding='UTF-8') as f:
        f.write(' '.join(result))
