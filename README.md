# json_conf_autoref
JSON extension for configuration files.



<a name="Version" />

## Version

0.1.5



<a name="Description" />

## Description

This module takes advantage from JSON that have a data strucutre similar to Python as a usual JSON file except that is allowed to create **variables** and refer to this variables in any part of the JSON file, following the rules at below:

* Variables reference example: `"${name_of_some_variable}"`;

* Variables **must** be referenced inside a string;

* Variable is **always** a reference to a **simple value**! **Never** an complex/neasted structures or lists!;

* You can concatenate variables

  Ex.: `"some_external_value${variable1}${variable2}"`;
  
* Variables inside arrays is **experimental**

  ```json
  "my_array":[1,2,"${some_variable}","abc",3.2]
  ```

* You can use dots '.' to refer to a sublevels inside JSON data:

  ```
  {
  	"level1":{
  		"level2":{
  			"level3":"some-value"
  		}
  	},
  	"another-var":"${level1.level2.level3}"
  }
  ```

* You **can't** use variables on keys

  ```json
  {
     "var": "Hey!",
     "${var}": "something else"
  }
  ```

  This will crash!



See more examples in the session [How to use](#How-to-use)



<a name="Requirements" />

## Requirements

Python, version 3.6 or later

pip

pytest



<a name="Installing" />

## Installing



### Git way

`git clone https://github.com/bang/json-conf-autoref.git`


then

`$ cd json-conf-autoref && python -m pip install -r requirements.txt`

then

`$ python setup.py pytest`

**If all it's ok**, then

`$ python setup.py install`

done!



### pip way

`python -mpip install json_config_autoref`

or

`python -mpip install json_config_autoref --user`



<a name="Features" />

## Features

* JSON key reference in any place of the structured;
* Supports environment variables with **restrictions**(See 'Limitations' topic);



<a name="How-to-use" />

## How to use



#### Create a JSON file. I called this one at below 'default.json':

```json
{
    "project-name":"fantastic-project",
    "hdfs-user":"john",
    "hdfs-base":"/usr/${hdfs-user}/${project-name}"
  
}
```



### Loading configuration data with `json_conf_autoref` module

```python
import json_conf_autoref as jca

# Loading from file
conf = jca.process(file='default.json')

# Alternatively, you can load from a string
jstr = """{
    "project-name":"fantastic-project",
    "hdfs-user":"john",
    "hdfs-base":"/usr/${hdfs-user}/${project-name}"
 }"""
conf = jca.process(json_string=)

# Showing config with all references replaced
jca.show(conf)
   
```



Result:

```json
{
    "hdfs-base": "/usr/john/fantastic-project",
    "hdfs-user": "john",
    "project-name": "fantastic-project"
}
```

What happened?

For the 'hdfs-base' value, the reference `${hdfs-user}`(is a reference for the key 'hdfs-user') was replaced by 'john'(value of the key 'hdfs-user'. Simple like that! If you have a key and a simple value, you can refere in another place only using the char '$' + *{name of the key between brakets}* that have the value you want. Of course, if you refere to a variable that not exists a exception will be trhown.

Now, let's complicate the *default.json* file a little bit, using reference to another reference using `$hdfs-base` referencing another reference.

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/${hdfs-user}/${project-name}"
    ,"hdfs-paths":{
        "incoming":"${hdfs-base}/incoming"
        ,"processing":"${hdfs-base}/processing"
        ,"processed":"${hdfs-base}/processed"
        ,"rejected":"${hdfs-base}/rejected"
    }
    
}
```



You can use another references mixing in simple values. In this case, the key "incoming", for example, has on config file the reference `${hdfs-base}` whose the original value has two another reference(`${hdfs-user}` and `${project-name}`). 

Now, loading the data from file with the same code as the example before

```python
import json_conf_autoref as jca

# Loading from file
conf = jca.process(file='default.json')

# Showing all vars from conf
jca.show(conf)
```



Result

```json
{
    "hdfs-base": "/usr/john/fantastic-project",
    "hdfs-paths": {
        "incoming": "/usr/john/fantastic-project/incoming",
        "processed": "/usr/john/fantastic-project/processed",
        "processing": "/usr/john/fantastic-project/processing",
        "rejected": "/usr/john/fantastic-project/rejected"
    },
    "hdfs-user": "john",
    "project-name": "fantastic-project"
}

```



**This will crash**!

```json
{
    "paths":{
        "path1":"/first/path"
        ,"path2":"/second/path"
    }
    ,"refer-test":${paths}
}
```

This crashes because '${paths}' is not between quotes and even was the case(between quotes), ${paths} is refering to a complex data and this is not allowed.



### Multiple-level references (dot-paths)

References by *dot-paths* is a reference to **existent paths** where any hirerchycal level division is represented by a dot char '.'. Ex:

Considering the same config file

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/${hdfs-user}/${project-name}"
    ,"hdfs-paths":{
        "incoming":"${hdfs-base}/incoming"
        ,"processing":"${hdfs-base}/processing"
        ,"processed":"${hdfs-base}/processed"
        ,"rejected":"${hdfs-base}/rejected"
    }
    
}
```

How to refer to 'incoming' key ? You can acess multiple levels of the structure using dots for each deep level you want to reach.

Example: Consider a JSON structure at below. Now, suppose to use a variable called "dot-path-example" that is on first level of this structure and value to reach is 'incoming', at below of 'hdfs-paths'. This is possible to access using dots like this: `"${hdfs-paths.incoming}"`

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/${hdfs-user}/${project-name}"
    ,"hdfs-paths":{
        "incoming":"${hdfs-base}/incoming"
        ,"processing":"${hdfs-base}/processing"
        ,"processed":"${hdfs-base}/processed"
        ,"rejected":"${hdfs-base}/rejected"
    },
 	"dot-path-example":"${hdfs-paths.incoming}"   
}
```



The loading code is the same as before. Showing the result:

```json
{
    "dot-path-example": "/usr/john/fantastic-project/incoming",
    "hdfs-base": "/usr/john/fantastic-project",
    "hdfs-paths": {
        "incoming": "/usr/john/fantastic-project/incoming",
        "processed": "/usr/john/fantastic-project/processed",
        "processing": "/usr/john/fantastic-project/processing",
        "rejected": "/usr/john/fantastic-project/rejected"
    },
    "hdfs-user": "john",
    "project-name": "fantastic-project"
}
```

As you can see, "dot-path-example" has exactly value as "hdfs-paths.incoming" key has. 



### Variables inside JSON arrays

Simple array example:

```json
{
    "some-key-reference":"some-value"
	,"the-list":[1,2,3,"yeah","${some-key-reference}"]
}
```



The loading code is the same as before. Showing the result:

```json
{
    "the-list": [
        1,
        2,
        3,
        "yeah",
        "some-value"
    ],
    "some-key": "some-value"
}
```



 

List on deep level:

```json
{
    "some-key-reference":"some-value"
	,"levels":{
        "level1":{
            "level2":{
                "level3":["something","${some-key-reference}"]
            }
        }
	}
}
```



Result:

```json
{
    "levels": {
        "level1": {
            "level2": {
                "level3": [
                    "something",
                    "some-value"
                ]
            }
        }
    },
    "some-key-reference": "some-value"
}
```



**This will crash**!

```
{
    "my-list":[1,2,3,"bla"]
    "ref-test":"${my-list}"
}
```

Again, you can't use reference to point to a substructure(a list), only to simple values.



### Environment variables(Please, see the restrictions below)

Ex:

```JSON
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/${hdfs-user}/${project-name}"
    ,"hdfs-paths":{
        "incoming":"${hdfs-base}/incoming"
        ,"processing":"${hdfs-base}/processing"
        ,"processed":"${hdfs-base}/processed"
        ,"rejected":"${hdfs-base}/rejected"
    },
    "test_env":"$ENV{SHELL} ---- $ENV{PATH}"
    
}
```

Results:

```JSON
{
    "hdfs-base": "/usr/john/fantastic-project",
    "hdfs-paths": {
        "incoming": "/usr/john/fantastic-project/incoming",
        "processed": "/usr/john/fantastic-project/processed",
        "processing": "/usr/john/fantastic-project/processing",
        "rejected": "/usr/john/fantastic-project/rejected"
    },
    "hdfs-user": "john",
    "project-name": "fantastic-project",
    "test_env": "/usr/bin/zsh ---- /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"
}
```

#### Restrictions

* Doesn't work on lists;
* Doesn't work on 'dot-paths'



### Comments

* is allowed using the chacacter '#';

* comment must not interfere on the references nor compromise the JSON document structure. 

Examples when comments are allowed:

```bash
{ #comment1
    "project-name":"fantastic-project",
#comment2    "test-ref":"#should-not-be-interpret-as-comment${project-name}",
    #comment3
    "another-var":"hey", #comment4
    "test-array":[1,2,3,4,"${project-name}",5,6,"${another-var}"],
    "inside-a-string":"#this is not considered as a comment!"
    #comment5
} #comment6

```



### Accessing data

Consider the our old and good 'default.json' file

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/${hdfs-user}/${project-name}"
    ,"hdfs-paths":{
        "incoming":"${hdfs-base}/incoming"
        ,"processing":"${hdfs-base}/processing"
        ,"processed":"${hdfs-base}/processed"
        ,"rejected":"${hdfs-base}/rejected"
    }
    
}
```



The `process` function returns always a `dict` object. So, only use the keys on dictionary!

```Python
# Using common dictionary acess 
hdfs_user = conf['hdfs-paths']['incoming'] # takes '/usr/john/fantastic-project/incoming' 
```





## Limitations



* **Reference to list/array index is not supported**: Something like `${some-list.3}` - intending to access position 3, considering that it's a single value is not possible;
* **Reference to complex data structured is not supported**: Reference to a hash or list is not supported(and never will);
* **Environment variables restrictions**: Not supported inside lists or 'dot-paths' yet;



## Change log

### 0.1.5

* Support for comments;
* Documentation fix;
* Starting a change log;
* Starting producing releases branches
* 90% test covered



### 0.1.3

* New support for environment variables;
* New unit tests.



## Bugs

https://github.com/bang/json-conf-autoref/issues



## Author

André Garcia Carneiro - andregarciacarneiro@gmail.com