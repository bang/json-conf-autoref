# coding: utf-8
"""json_conf_autoref

    Version
    -------
    0.0.4

    Description
    -----------

    This module is a config parser that works with JSON format. Content can come 
    from a JSON file or string. The module accepts variable definition inside the 
    JSON data just adding '$' character to refere to any key that exists inside 
    the JSON content.

    Examples
    --------

    # conf/default.json
    {
        "hdfs-user":"some_cool_guy"
        ,"hdfs-base":"hdfs://yourcompany.com/user/$hdfs-user/fantastic-project"

    }

    # code snipet - from JSON file
    import json_conf_autoref as jca

    conf = jca.process(file="conf/default.json")
    jca.show_conf() 

    Shows

    {
        "hdfs-base": "hdfs://yourcompany.com/user/some_cool_guy/fantastic-project",
        "hdfs-user": "some_cool_guy"
    }

    # From a JSON string

    my_json = '{"hdfs-user":"some_cool_guy","hdfs-base":"hdfs://yourcompany.com/user/$hdfs-user/fantastic-project"}

    conf = jca.process(json_string = my_json)

    Shows

    {
        "hdfs-base": "hdfs://yourcompany.com/user/some_cool_guy/fantastic-project",
        "hdfs-user": "some_cool_guy"
    }


    Limitations
    -----------

    There is no support for lists with variables. Maybe in the next version


"""
import json
import sys,os,re
from exceptions import *

__version__ = '0.0.4'


def __traverse_json(json_input,path):
    """A internal recursive function that goes through JSON hierarchical structure
    looking for variables inside values using regular expression and yields 
    a list of variables that it's found.

        Parameters
        ----------

        json_input: list or dict, requited
        Python data structure(list or dict) with JSON data

        path: str,required
        The start point in the JSON structure

        Yields
        -------

            First scenario - Not-list structure
            -----------------------------------
            A new recursive call to function passing the current path if value in some 
            point of structure not satisfies the requirements to replace variables to
            values

            or

            A key-value pair dictionary with 

            Second scenario - list structure
            --------------------------------
            Iterates the list and do the same thing in first scenario for each
            element of the list
        
    """
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            # Divides the structure keys with '/'. Familiar, huh?
            if isinstance(v,str) and re.search(r'^.*?(\$.+?)$',v):
                yield { '/'.join([path , k]) : v }
            else:
                # yields a new recursive call for __traverse passing 
                # the current value and current path level
                yield from __traverse_json(v, '/'.join([path , k]))
    elif isinstance(json_input, list):
        yield { path:json_input }


def __check_result(data):
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    #print("LOOKUPS: {}".format(str(lookups)))
    if len(lookups) == 0:
        return True
    ok = True
    for l in lookups:
        for k,v in l.items():
            if isinstance(v,list):
                for i in v:
                    #print("I: {}".format(str(i)))
                    if re.search(r'\$',str(i)):
                        return False
            elif re.search(r'\$',str(v)):
                return False
            else:
                return True
    return ok


def __get_from_path(data,path):
    levels = re.split(r'\.',path)
    if len(levels) == 0:
        levels = [path]

    value = None
    key = re.sub('^\$','',levels[0])
    value = data[key]
    #print("VALUE: {}".format(str(value)))
    if isinstance(value,list) or isinstance(value,dict):
        levels.pop(0)
        new_path = '.'.join(levels)
        new_data = value
        return __get_from_path(new_data,new_path)
    else:
        return value


def __replace_vars_list(data,path,element_path,position):
    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\$[\-\_A-Za-z\.]+[0-9]*)',str(element_path))
    if len(vars_to_replace) == 0 :
        vars_to_replace = re.findall(r'(\$[\-\_A-Za-z\.]+[0-9]*.*?$)',str(element_path))

    new_list = []

    # Transforming paths into a valid dictionary path
    transformed_path = ""
    for part in path:
        transformed_path += "['{}']".format(part)
    temp_flag = False

    # Just place the same value on the array(list) position
    if len(vars_to_replace) == 0:
        exec("data{}[{}] = element_path".format(str(transformed_path),str(position)))

    else:
        temp_flag = True
        #print("WHERE: {}".format(str(element_path)))
        # Getting values for replacing
        for v in vars_to_replace:
            # Removing stupid chars(and content after it) that could mess 
            # the reference names.
            # Don't know if this regex is enough yet. For now, this is it!
            v = re.sub(r'[\:\,\ \@\#\*\&\%\/].*?$','',str(v))
            #v = re.sub(r'.*?(\$.+?)$','',v)

            value = __get_from_path(data,v)
            what = re.sub(r'\$',"\\\$",v)
            to = value 
            where = element_path
            exec("data{}[{}] = re.sub(r'{}','{}','{}')" \
                .format(
                        transformed_path
                        ,position
                        ,what
                        ,to
                        ,where
                )
            )
    return data



def __replace_vars_single(data,path,element_path):
    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\$[\-\_A-Za-z\.0-9]+[0-9]*)',str(element_path))
    if len(vars_to_replace) == 0 :
        vars_to_replace = re.findall(r'(\$[\-\_A-Za-z\.0-9]+[0-9]*.*?$)',str(element_path))
    print("VARS_TO_REPLACE: {}".format(str(vars_to_replace)))
    # Transforming paths into a valid dictionary path
    transformed_path = ""
    for part in path:
        transformed_path += "['{}']".format(part)

    # Getting values for replacing
    for v in vars_to_replace:
        if v == '':
            continue
        # Removing stupid chars(and content after it) that could mess 
        # the reference names.
        # Don't know if this regex is enough yet. For now, this is it!
        v = re.sub(r'[\:\,\ \@\#\*\&\%\/].*?$','',str(v))
        #v = re.sub(r'.*?(\$.+?)$',r'\1',v)
        print("V: {}".format(str(v)))
        # For variables that represents paths. Like "$pathLv1.pathLv2.pathLvN"
        if re.search(r'\.',v):
            value_path = re.split(r'\.',v)
            var_path = ""
            #print("VALUE_PATH: {}".format(str(value_path)))
            for part in value_path:
                # Ignoring crap. XHG
#                part = re.sub("[\,\ \:]+.+?$",'',str(part))
                # Preparing var
                prepared_part = re.sub(r'^\$','',part)
                var_path += "['{}']".format(prepared_part)

            # Getting value for 'doted' variables
            print("VAR_PATH: {}".format(var_path))
            value = eval("data{}".format(var_path))

        # For variables that is defined on root of config content
        else:
            # So, var is in the root path
            key = re.sub(r'\$','',v)
            print("KEY: {}".format(key))
            value = data[key]

        # Preparing 'v' for regex
        v = re.sub(r'\$','\\\$',v)

        # Storing regex replacement result
        replacement = eval("re.sub(r''+ v, value, element_path)")
        
        # updating element_path with regex replacement result
        element_path = replacement

        # Finally replacing values in data
        exec("data{} = replacement".format(transformed_path))

    return data


def __replace_vars_factory(data,path,element_path,type):
    if type == 'list':
        position = 0
        for e in element_path:
            data = __replace_vars_list(data,path,e,position)
            position += 1
    elif type == 'single':
        data = __replace_vars_single(data,path,element_path)
    else:
        raise InvalidParam("type must be 'list' or 'single'!")

    return data



def __analyze(data):
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    for l in lookups:
        for rawPath,lookup in l.items():
            Items = re.split(r'/',rawPath)
            if Items[0] == '':
                Items.pop(0)

            # What's it values?
            element_path = None
            path = []
            for i in Items:
                if(element_path == None):
                    element_path = data[i]
                else:
                    element_path = element_path[i]
                path.append(i)

            # print("ELEMENT-PATH: {}".format(str(element_path)))
            if isinstance(element_path,list):
                data = __replace_vars_factory(data,path,element_path,'list')
            else:
                data = __replace_vars_factory(data,path,element_path,'single')


    return data



def show_conf(data):
    print(str(json.dumps(data,indent=4,sort_keys=True)))


def process(json_string=None,file=None):
    data = None

    # Checking parameters
    if not json_string and not file:
        raise InvalidParam("No input data! You must define 'json_string' or 'file' parameter")

    if file:
        data = {}
        with open(file) as f:
            data = json.load(f)
    else:
        try:
            data = json.loads(json_string)
        except ValueError as e:
            print("invalid JSON!")
            raise

    # Because of random key acess, some variables could not be processed. So,
    # must run again until this happens. But a limit of 5 iterations was defined
    # to avoid infinit running.
    data = __analyze(data)
    if not __check_result(data):
        limit = 5
        curr_time = 0
        while not __check_result(data):
            data = __analyze(data)
            if curr_time >= limit:
                raise LimitException("Fatal! Can't process this data! Please, report this issue sending the config data!")
            curr_time += 1

    return data


def get(data,path):
    data_from_path = {}

    if not data:
        raise invalidParam("'data' param is invalid!")

    if not path:
        raise PathNotDefined("Path is invalid! Expecting something like 'some-key.level1.level2 ... .levelN'")

    elif re.search(r'\.',path):
        levels = split(r'\.',path)
        keys = ''
        for level in levels:
            keys += "['{}']".format(str(level))
        data_from_path = eval("data{}".format(key))
    else:
        data_from_path = data[path]

    return data_from_path

def main():

    data = process( file='default.json')
    show_conf(data)



if __name__ == '__main__':
    main()



