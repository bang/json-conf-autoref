import os
import sys
import pytest
import json_conf_autoref as jc

# Comments tests
def test_comments_on_string():
    js_string = """
    { #comment1
        "project-name":"fantastic-project",
    #comment2    "test-ref":"#should-not-be-interpret-as-comment${project-name}",
        #comment3
        "another-var":"hey", #comment4
        "test-array":[1,2,3,4,"${project-name}",5,6,"${another-var}"],
        "inside-string":"#this is not considered a comment!"
        #comment5
    } #comment6"""
    conf = jc.process(json_string=js_string)
    assert conf['another-var'] == 'hey'
    assert conf['inside-string'] == "#this is not considered a comment!"
    assert conf['project-name'] == "fantastic-project"
    array_comparing = [
        1,
        2,
        3,
        4,
        "fantastic-project",
        5,
        6,
        "hey"
    ]
    assert conf['test-array'] == array_comparing

def test_comments_on_file():
    # Simple test. No vars, one value
    os.environ['MY_VAR1']='test1'
    conf = jc.process(file='config.json')
    assert conf['another-var'] == 'hey'
    assert conf['inside-string'] == "#this is not considered a comment!"
    assert conf['project-name'] == "fantastic-project"
    array_comparing = [
        1,
        2,
        3,
        4,
        "fantastic-project",
        5,
        6,
        "hey"
    ]
    assert conf['test-array'] == array_comparing
    
