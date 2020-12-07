import os
import sys
import pytest
import json_conf_autoref as jc

# Environment variable tests

def test_common_use():
  # Simple test. No vars, one value
  os.environ['MY_VAR1']='test1'
  js_string = """
    {
      "no-var-test":"works",
      "test-env-var":"$ENV{MY_VAR1}"
    }"""
  conf = jc.process(json_string=js_string)
  assert conf['no-var-test'] == 'works'
  assert conf['test-env-var'] == 'test1'


def test_concatenation():
  # Simple test. No vars, one value
  os.environ['MY_VAR1']='test1'
  os.environ['MY_VAR2']='test2'
  js_string = """
    {
      "no-var-test":"works",
      "test-env-var":"$ENV{MY_VAR1}$ENV{MY_VAR2}"
    }"""
  conf = jc.process(json_string=js_string)
  assert conf['no-var-test'] == 'works'
  assert conf['test-env-var'] == 'test1test2'


def test_deep():
  # Simple test. No vars, one value
  os.environ['MY_VAR1']='test1'
  os.environ['MY_VAR2']='test2'
  js_string = """
    {
      "no-var-test":"works",
      "level1":{
        "level2":{
            "level3":"$ENV{MY_VAR1}"
        }
      }
    }"""
  conf = jc.process(json_string=js_string)
  assert conf['no-var-test'] == 'works'
  assert conf['level1']['level2']['level3'] == 'test1'


def test_deep_with_concatenation():
  # Simple test. No vars, one value
  os.environ['MY_VAR1']='test1'
  os.environ['MY_VAR2']='test2'
  js_string = """
    {
      "no-var-test":"works",
      "level1":{
        "level2":{
            "level3":"$ENV{MY_VAR1}$ENV{MY_VAR2}"
        }
      }
    }"""
  conf = jc.process(json_string=js_string)
  assert conf['no-var-test'] == 'works'
  assert conf['level1']['level2']['level3'] == 'test1test2'


def test_deep_with_concatenation2():
  # Simple test. No vars, one value
  os.environ['MY_VAR1']='test1'
  os.environ['MY_VAR2']='test2'
  js_string = """
    {
      "no-var-test":"works",
      "level1":{
        "level2":{
            "level3":"$ENV{MY_VAR1}--- # foobar$ENV{MY_VAR2}"
        }
      }
    }"""
  conf = jc.process(json_string=js_string)
  assert conf['no-var-test'] == 'works'
  assert conf['level1']['level2']['level3'] == 'test1--- # foobartest2'
