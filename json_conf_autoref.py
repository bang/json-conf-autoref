# coding: utf-8
"""json_conf_autoref

    Version
    -------
    0.0.8

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
    jca.show(conf)

    Shows

    {
        "hdfs-base": "hdfs://yourcompany.com/user/some_cool_guy/fantastic-project",
        "hdfs-user": "some_cool_guy"
    }

    # From a JSON string

    my_json = '{"hdfs-user":"some_cool_guy","hdfs-base":"hdfs://yourcompany.com/user/${hdfs-user}/fantastic-project"}

    conf = jca.process(json_string = my_json)

    jca.show(conf)

    Shows

    {
        "hdfs-base": "hdfs://yourcompany.com/user/some_cool_guy/fantastic-project",
        "hdfs-user": "some_cool_guy"
    }

    # Vars
    {
        "project-name":"fantastic-project"
        "hdfs-base": "hdfs://yourcompany.com/user/some_cool_guy/${project-name}",
        "hdfs-user": "some_cool_guy"
    }

    # Vars inside lists(EXPERIMENTAL)

    my_json = '{"hdfs-user":"joe", "system-users":["${hdfs-user}","mary","lucca"] }'

    conf = jca.process(json_string = my_json)

    jca.show(conf)


    Shows

    '{"hdfs-user":"joe", "system-users":["joe","mary","lucca"] }'


    Limitations
    -----------

    Vars on list is experimental and could crash in "not-mapped" situations.


"""
import json
import sys,os,re
from exceptions import *

__version__ = '0.0.8'


__author__ = "André Carneiro"


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
            if isinstance(v,str) and re.search(r'^.*?(\${.+?}).*?$',v):
                yield { '/'.join([path , k]) : v }
            else:
                # yields a new recursive call for __traverse passing
                # the current value and current path level
                yield from __traverse_json(v, '/'.join([path , k]))
    elif isinstance(json_input, list):
        yield { path:json_input }


def __check_result(data):
    """Returns False if exists some variable under processing results structure.
        Otherwise returns True

        Parameters
        ----------
        data : dict
            Processing result dictionary

        Returns
        -------
        False
            If there is variables not replaced by their respective values.

        True
            Otherwise


    """
    lookups = []
    for _ in __traverse_json(data,''):
        lookups.append(_);

    if len(lookups) == 0:
        return True
    ok = True
    for l in lookups:
        for k,v in l.items():
            if isinstance(v,list):
                for i in v:
                    if re.search(r'\${.+?}*',str(i)):
                        return False
            elif re.search(r'\${.+?}*',str(v)):
                return False
            else:
                return True
    return ok


def __get_from_path(data,path):
    """Recovers a value that is referenced by a var under 'dot-path'("Ex: "$hdfs-paths.incoming").

        Parameters
        ----------
        data : dict
            Full JSON data under dictionary

        path : str
            A 'dot-path' var string


        Returns
        -------
        A single value of a var.


    """
    levels = re.split(r'\.',path)
    if len(levels) == 0:
        levels = [path]

    value = None
    key = re.sub(r'^\${','',levels[0])
    key = re.sub(r'}','',key)
    value = data[key]
    if isinstance(value,list) or isinstance(value,dict):
        levels.pop(0)
        new_path = '.'.join(levels)
        new_data = value
        return __get_from_path(new_data,new_path)
    else:
        return value


def __replace_vars_list(data,path,element_path,position):
    """Replace vars under single values(strings and numbers for example).

        Parameters
        ----------
        data : dict
            JSON structure(full of it) transcripted to a dictionary

        path : list
            All path to an target element

        element_path : str
            The full path element string of JSON structure

        position : int
            The position in the list that is beeing analyzed


        Returns
        -------
        A dictionary with the processing result
    """

    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\${.+?})',str(element_path))
    new_list = []

    # Transforming paths into a valid dictionary path
    transformed_path = ""
    for part in path:
        transformed_path += "['{}']".format(part)
    # temp_flag = False

    # Just place the same value on the array(list) position
    if len(vars_to_replace) == 0:
        exec("data{}[{}] = element_path".format(str(transformed_path),str(position)))

    else:

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
            cmd = f"data{transformed_path}[{position}] = re.sub(r'{what}',\'{to}\',\"{where}\")"
            exec(cmd)
    return data


def __replace_vars_single(data,path,element_path):
    """Replace vars under single values(strings and numbers for example).

        Parameters
        ----------
        data : dict
            JSON structure(full of it) transcripted to a dictionary

        path : list
            All path to an target element

        element_path : str
            The full path element string of JSON structure


        Returns
        -------
        A dictionary with the processing result



    """
    # Separating variables from the rest of the path
    vars_to_replace = re.findall(r'(\$\{.+?\})',str(element_path))

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
        # For variables that represents paths. Like "$pathLv1.pathLv2.pathLvN"
        key = value = ''
        if re.search(r'\.',v):
            value_path = re.split(r'\.',v)
            var_path = ""

            for part in value_path:
                # Preparing var
                prepared_part = re.sub(r'^\${','',part)
                prepared_part = re.sub(r'}$','',prepared_part)
                var_path += "['{}']".format(prepared_part)

            # Getting value for 'doted' variables
            value = eval("data{}".format(var_path))

        # For variables that is defined on root of config content
        else:
            # So, var is in the root path
            key = re.sub(r'\${','',v)
            key = re.sub(r'}','',key)
            value = data[key]

        # Preparing 'v' for regex
        v = re.sub(r'\$', '\\\$',v)

        # Storing regex replacement result
        replacement = eval("re.sub(r''+ v, value, element_path)")

        # updating element_path with regex replacement result
        element_path = replacement

        # Finally replacing values in data
        exec("data{} = replacement".format(transformed_path))


    return data


def __replace_vars_factory(data,path,element_path,type):
    """A factory function when the goes is decide what kind
        of processing data must be submited. The possibilities
         of 'type' are determinated by a string that must contain only one
        of two values:

        * single: a single value(string or numbers)

        * list: single values inside lists(arrays)

        Parameters
        ----------
        data : dict
            JSON structure(full of it) transcripted to a dictionary

        path : list
            All path to an target element

        element_path : str
            The full path element string of JSON structure

        type : str
            The type of vars replacing. Must be 'single' or 'list'


        Returns
        -------
        A dictionary with the processing result


        Exceptions
        ----------
        InvalidParam
            When type was passed as something different than 'single' nor 'list'


    """
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
    """Applies the 'traverse' on JSON structure(here is a dictionary) and submit
        data to __replace_vars_factory to replace values under this structure
        depending the kind of it(single or list) and return the results as a
        dictionary.

        Parameters
        ----------
        data : dictionary
        JSON structure transcripted to a dictionary


        Returns
        -------
        A dictionary with the processing results



    """
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

            if isinstance(element_path,list):
                data = __replace_vars_factory(data,path,element_path,'list')
            else:
                data = __replace_vars_factory(data,path,element_path,'single')

    return data


def show(data):
    """Shows the results of JSON processing from a config data
    passing the 'process' resultant dictionary on the screen

        Parameters
        ----------
        data : dictionary
                The dictionary generated after 'process'
                function call

        Returns
        -------
        Nothing


    """
    print(str(json.dumps(data,indent=4,sort_keys=True)))


def process(json_string=None,file=None):
    """Reads the JSON from file or string. Then, iterates the processing
        using __analyze and __check_results internal functions to evaluate if
        there is some variable in deep structure needs to be replaced and/or
        if the times to try is over or not.

        Returns a dictionary with all data processed.


        Parameters
        ----------
        json_string : str or None

        file : str or None


        Returns
        -------
        A dictionary with processed config data


        Exceptions
        ----------

        ValueError
            When JSON reading fails.

        LimitException
            When iterations exceeds the iterations times limits(max 5x)

        InvalidParam
            When 'json_string' and 'file' params are not set

    """


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
            print("JSON error! {}".format(str(e)))
            raise

    # Because of random key acess, some variables could not be processed. So,
    # must run again until this happens. But a limit of 5 iterations was defined
    # to avoid infinit recursion.
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


if __name__ == '__main__':
    pass


class LimitException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
