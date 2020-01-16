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
        ,"key3":"$key1$key2"
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
            ,"level2-var-reference":"$levels.level1.level2-var"
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
                "concat":"$key1$key2"
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
                "concat":"$key1/$key2#$key3:33"
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
    assert str(conf['key1']) == '[1,2,3,"works"]'


