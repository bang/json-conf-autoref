# coding: utf-8
"""json_conf_autoref

    Version
    -------
    0.0.3

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

__version__ = '0.0.3'


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

            Raises
            ------

        
    """
    if isinstance(json_input, dict):
        # print("dict")
        for k, v in json_input.items():
            # Divides the structure keys with '/'. Familiar, huh?
            if isinstance(v,str) and re.search(r'^.*?(\$.+?)$',v):
                yield { '/'.join([path , k]) : v }
            else:
                # yields a new recursive call for __traverse passing 
                # the current value and current path level
                yield from __traverse_json(v, '/'.join([path , k]))
    elif isinstance(json_input, list):
        for item in json_input:
            if isinstance(item,str) and re.search(r'^.*?(\$.+?)$',item):
                yield { path : item }
            else:
                yield from __traverse_json(item,path)


def __check_result(data):
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    check = False
    if len(lookups) == 0:
        check = True

    return check

def __replace_vars_list(data,path,element_path):
    # Still thinking how... 
    # print("WARNING: List with variables is not supported in this version! Sorry!")
    
    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\$[\-\-A-Za-z\.]+[0-9]*)',element_path)

    # Transforming paths into a valid dictionary path
    transformed_path = ""
    for part in path:
        transformed_path += "['{}']".format(part)

    # Getting values for replacing
    values_list = []
    for v in vars_to_replace:
        # For variables that represents paths. Like "$pathLv1.pathLv2.pathLvN"
        if re.search(r'\.',v):
            value_path = re.split(r'\.',v)
            var_path = ""
            for part in value_path:
                prepared_part = re.sub(r'\$','',part)
                var_path += "['{}']".format(prepared_part)
            # Getting value for 'doted' variables
            value = eval("data{}".format(var_path))

        # For variables that is defined on root of config content
        else:
            # So, var is in the root path
            key = re.sub(r'\$','',v)
            value = data[key]

        # Preparing 'v' for regex
        v = re.sub(r'\$','\\\$',v)
        new_value = re.sub(r''+ v, value, element_path)
        print("new_value: {}".format(new_value))
        values_list.append(new_value)

    # Finally replacing
    exec("data{} = values_list".format(transformed_path))

    return data


def __replace_vars_single(data,path,element_path):
    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\$[\-\-A-Za-z\.]+[0-9]*)',element_path)

    # Transforming paths into a valid dictionary path
    transformed_path = ""
    for part in path:
        transformed_path += "['{}']".format(part)

    # Getting values for replacing
    for v in vars_to_replace:
        # For variables that represents paths. Like "$pathLv1.pathLv2.pathLvN"
        if re.search(r'\.',v):
            value_path = re.split(r'\.',v)
            var_path = ""
            for part in value_path:
                prepared_part = re.sub(r'\$','',part)
                var_path += "['{}']".format(prepared_part)
            # Getting value for 'doted' variables
            value = eval("data{}".format(var_path))

        # For variables that is defined on root of config content
        else:
            # So, var is in the root path
            key = re.sub(r'\$','',v)
            value = data[key]

        # Preparing 'v' for regex
        v = re.sub(r'\$','\\\$',v)

        # Finally replacing 
        exec("data{} = re.sub(r''+ v, value, element_path)".format(transformed_path))

    return data


def __replace_vars_factory(data,path,element_path,type):
    if type == 'list':
        for e in element_path:
            data = __replace_vars_list(data,path,e)
    elif type == 'single':
        data = __replace_vars_single(data,path,element_path)
    else:
        raise InvalidParam("type must be 'list' or 'single'!")

    return data


def __analyze(data):
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    data_map = []
    last_key = ''
    for l in lookups:
        #print("L: {}".format(str(l)))
        for key,value in l.items():
            # Allowing variables values access
            path_parts = re.split(r'/',key)
            path_parts.pop(0) # removes '' from first element
            json_path = ''
            for p in path_parts:
                json_path += "['{}']".format(p)

            print("\nJSON_PATH: {}".format(json_path))
            print("KEY: {}".format(str(key)))
            print("VALUE: {}".format(str(value)))

            # Finding all variables in 'value'
            vars_to_find = re.findall(r'(\$[\-\-A-Za-z\.]+[0-9]*)',value)
            if len(vars_to_find):
                print("VARS_TO_FIND: {}".format(str(vars_to_find)))
                
                for v in vars_to_find:
                    noref_var = re.sub(r'^\$','',v)
                    # Checking if variable reference is from another path
                    if re.search(r'\.',noref_var):
                        var_doted_path = re.split('\.',noref_var)
                        var_path = ""
                        for p in var_doted_path:
                            var_path += "['{}']".format(p)
                        
                        # Getting the value of the variable
                        print("data{} = data{}".format(json_path,var_path))
                    else:
                        var_path = "['{}']".format(noref_var)
                        # Getting the value of the variable
                        prepared_var = re.sub(r'\$',"\\\$",v)
                        exec("data{} = re.sub(r'{}',data{},v)".format(json_path,prepared_var,var_path))

        print("NEW_DATA: {}".format(data))

    #         if last_key == key:
    #             pass
    #         else:
    #             data_map[key] = value
    # print("DATA_MAP: {}".format(str(data_map)))
    sys.exit(0)

def __analyzeOLD(data):
#    print("DATA: {}".format(data))
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    # print("lookups: {}".format(lookups))
    for l in lookups:
        for rawPath,lookup in l.items():
            Items = re.split(r'/',rawPath)
            Items.pop(0)

            # print("ITEMS: {}".format(Items))

            # What's it values?
            element_path = None
            path = []
            for i in Items:
                if(element_path == None):
                    element_path = data[i]
                else:
                    element_path = element_path[i]
                path.append(i)

            print("element_path: {}".format(str(element_path)))
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
    # if not __check_result(data):
    #     limit = 5
    #     curr_time = 0
    #     while not __check_result(data):
    #         data = __analyze(data)
    #         if curr_time >= limit:
    #             raise LimitException("Fatal! Can't process this data! Please, report this issue sending the config data!")
    #         curr_time += 1

    return data



def main():

    data = process(json_string = """{
        "hdfs-user":"andre"
        ,"hdfs-base":"/user/$hdfs-user"
        ,"list-with-vars":["$hdfs-user","$hdfs-base"]
        ,"paths":{
            "incoming":"$hdfs-base/incoming"
        }
        ,"more-than-one":"$hdfs-user,$hdfs-base"
    }""")
    show_conf(data)



if __name__ == '__main__':
    main()

#        ,"hdfs-base":"hdfs://yourcompany.com/user/$hdfs-user/fantastic-project"

        # ,"hdfs-base":"user/$hdfs-user/something-else"
        # ,"paths":{
        #     "incoming":"$hdfs-base/incoming"
        # }
        # ,"deep-test":"$paths.incoming"


