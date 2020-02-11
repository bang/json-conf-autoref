# json_conf_autoref
Manipulate JSON config files with internal variables



## VERSION

0.0.6-rc1



## Intro

This module takes advantage from JSON that have a data strucutre similar to Python as a usual json file except that accept variable references inside the structure **under the following rules:**



1. All references must be within **strings**;
2. The reference is **always** to a **key, dot-path or another existent reference**;
3. The character used to build references to a key is **'$'**;
4. References must **always**  "point" to simple values( strings, numbers etc) and never other structures( common lists or indexed lists knowing in Python as dictionaries ) or just another reference(Ex: $some-reference);
5. You can use more than one reference in the same string folowing the rules above



## Requirements

Python3

pip



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





## HOW TO USE



#### Create a JSON file. I called this one at bellow 'default.json':

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
  
}
```



### Loading configuration data with `json_conf_autoref` module

```python
import json_conf_autoref as jca

# Loading from file
conf = jca.process(file='default.json')

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

For the 'hdfs-base' value, the reference `$hdfs-user`(is a reference for the key 'hdfs-user') was replaced by 'john'(value of the key 'hdfs-user'. Simple like that! If you have a key and a simple value, you can refere in another place only using the char '$' + *name of the key* that have the value you want. Of course, if you refere to a variable that not exists a exception will be trhown.



Now, let's complicate the *default.json* file a little bit, using reference to another reference using `$hdfs-base` referencing another reference.

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
    ,"hdfs-paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
    
}
```



You can use another references mixing in simple values. In this case, the key "incoming", for example, has on config file the reference `$hdfs-base` whose the original value has two another reference(`$hdfs-user` and `$project-name`). 



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
    ,"refer-test":$paths
}
```

This crashes because breaks the fourth rule defined on *Intro* section: '*References must **always**  "point" to simple values( strings, numbers etc) and never other structures( common lists or indexed lists knowing in Python as dictionaries ) or just another reference(Ex: $some-reference)*'



Since the reference `$paths` doesn't points to a simple value but to an sub-structure, this can't be used as a reference. So, crashes!





### Multiple references levels(dot-paths)

References by *dot-paths* is a reference to **existent paths** where any hirerchycal level division is represented by a dot char '.'. Ex:



Considering the same config file

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
    ,"hdfs-paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
    
}
```



How to refer to 'incoming' key ? You can acess multiple levels as reference using a simple(and not new) concept that I simply decided to name as ***dot-paths***. As the name is suggesting, a *dot-path* is a path whose levels are marked/identified separating each path level using dots. Ex: If you want access the "incoming" key, the *dot-path* for this is `$hdfs-paths.incoming`.



Referencing "incoming" key in a new key called `dot-path-example`

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
    ,"hdfs-paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
 	,dot-path-example:$hdfs-paths.incoming   
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



Indirect references over *dot-path* **is not allowed**! 

**This reference will not work**

```
"doesnt-work":"$hdfs-base.incoming"
```





### Lists(experimental) 

Simple list example:

```json
{
    "some-key-reference":"some-value"
	,"the-list":[1,2,3,"yeah","$some-key-reference"]
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
                "level3":["something","$some-key-reference"]
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
    "ref-test":"$my-list"
}
```

Again, you can't use reference to point to a substructure(a list), just to single values.



**This will crash!**

```json
    {
        "key1":"test1"
        ,"key2":"test2"
        ,"key3":{
            "level1":{
                "level2":{
                    "level2-list":["$key1$key2","$key3.level1.level2.value"]
                    ,value="some value"
                }
            ,"level1-value":"This is level1"
            }
        }
    }
```

The *dot-path* is not working on lists yet.





### Accessing data



Consider the our old and good 'default.json' file

```json
{
    "project-name":"fantastic-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
    ,"hdfs-paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
    
}
```



To access data is just do with any Python data structure.

```Python
# Using common dictionary acess 
hdfs_user = conf['hdfs-paths']['incoming'] # takes 'john' 


```



### Setting values

Not supported 



### Accessing list position values for references

Ex: Reference beeing something like `$some-list.3` - to try to access position 3, considering that it's a single value.



Not supported yet





## Bugs



Please, report another bugs to andregarciacarneiro@gmail.com





## Author

André Garcia Carneiro - andregarciacarneiro@gmail.com

