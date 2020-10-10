import sys
import pytest
import json_conf_autoref as jc



def test_simple_no_vars():
    # Simple test. No vars, one value
    js_string = """
    {
        "no-var-test":"works"
    }"""

    conf = jc.process(json_string=js_string)
    assert conf['no-var-test'] == 'works'

    # More than one value
    js_string = """
    {
        "key1":"works"
        ,"key2":"works too"
        ,"key3":"all good!"
    }"""

    conf = jc.process(json_string=js_string)
    assert conf['key1'] == 'works'
    assert conf['key2'] == 'works too'
    assert conf['key3'] == 'all good!'


def test_simple_var_concatenation():
    js_string = """
    {
        "key1":"works"
        ,"key2":"works too"
        ,"key3":"${key1}${key2}"
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['key3'] == "worksworks too"


def test_hirerarchy_no_vars_on_values():
    # Hierarchy with no var references
        js_string = """
        {
            "key1":"works"
            ,"key2":"works too"
            ,"key3":"all good!"
            ,"levels":{
                "level1":{
                    "level2-var":"you're on level 2"
                }
            }
            ,"level2-var-reference":"${levels.level1.level2-var}"
        }"""

        conf = jc.process(json_string=js_string)
        assert conf['level2-var-reference'] == "you're on level 2"


def test_hierarchycal_var_concatenation():
    js_string = """
    {
        "key1":"works"
        ,"key2":"works too"
        ,"levels":{
            "level1":{
                "concat":"${key1}${key2}"
            }
        }
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['levels']['level1']['concat'] == "worksworks too"


def test_hierarchycal_var_and_chars_concatenation():
    js_string = """
    {
        "key1":"works"
        ,"key2":"works too"
        ,"key3":"works fine"
        ,"levels":{
            "level1":{
                "concat":"${key1}/${key2}#${key3}:33"
            }
        }
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['levels']['level1']['concat'] == "works/works too#works fine:33"


def test_list_no_vars():
    js_string = """
    {
        "key1":[1,2,3,"works"]
        ,"key2":"works too"
        ,"key3":"works fine"
    }"""
    conf = jc.process(json_string=js_string)
    if str(conf['key1'][0]) == "1" and \
        str(conf['key1'][1]) == "2" and \
        str(conf['key1'][2]) == "3" and \
        str(conf['key1'][3]) == "works":
        assert True


def test_list_sub_no_vars():
    js_string = """
    {
        "key1":{
            "key2":[1,2,3,"works"]
            ,"key3":{
                "key4":[4,5,6,"This is level 4"]
            ,"level2":"This is level 2"
            }
        }
    }"""
    conf = jc.process(json_string=js_string)
    print(str(conf['key1']))
    assert str(conf['key1']['key2'][3]) == "works"


def test_list_vars():
    js_string = """
    {
        "key1":"something"
        ,"key2":[1,2,3,"${key1}"]
    }"""
    conf = jc.process(json_string=js_string)
    print(str(conf['key2']))
    assert str(conf['key2'][3]) == "something"


def test_list_sub_with_vars():
    js_string = """
    {
        "key1":{
            "key2":[1,2,3,"works"]
            ,"key3":{
                "key4":[4,5,6,"${var_to_list}"]
            }
            ,"level2":"This is level 2"

        }
        ,"var_to_list":"test"
    }"""
    conf = jc.process(json_string=js_string)
    print("FOOOOO: {}".format(str(conf['key1']['key3']['key4'])))
    assert str(conf['key1']['key3']['key4'][3]) == "test"


def test_simple_concat_vars():
    js_string = """
    {
        "key1":"test1"
        ,"key2":"test2"
        ,"key3":"${key1}${key2}"
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['key3'] == "test1test2"


def test_deep_concat_vars():
    js_string = """
    {
        "key1":"test1"
        ,"key2":{
            "level2-1":"this is ${key1}"
            ,"level2-2":"hey"
            ,"level2-3":"${key1}${key3}"
            ,"level2-4":"${key1}${key2.level2-2}"
        }
        ,"key3":"test2"
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['key2']["level2-1"] == "this is test1"
    assert conf['key2']["level2-3"] == "test1test2"
    assert conf['key2']["level2-4"] == "test1hey"


def test_list_concat_vars():
    js_string = """
    {
        "key1":"test1"
        ,"key2":"test2"
        ,"key3":["${key1}${key2}"]
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['key3'][0] == "test1test2"


def test_list_concat_deep_vars():
    js_string = """
    {
        "key1":"test1"
        ,"key2":"test2"
        ,"key3":{
            "level1":{
                "level2":{
                    "level2-list":["${key1}${key2}"]
                }
            ,"level1-value":"This is level1"
            }
        }
    }"""
    conf = jc.process(json_string=js_string)
    assert conf['key3']['level1']['level2']['level2-list'][0] == "test1test2"
