# json-conf-autoref
Manipulate JSON config files with internal variables



## VERSION

0.0.4 - unstable



## Intro

This module takes advantage from JSON that have a data strucutre similar to Python as a usual json file except that accept variable references inside the structure **under the following rules:**



1. All references are **strings** inside JSON file
2. The reference is **always** to a **key or a variable-path**. **Never** to other values! See more details on *How to use* section
3. The character used to make a reference for a key in JSON is **'$'**



For now this is **not** a object oriented module. Maybe in the future.





## Install



### Git

`git clone https://github.com/bang/json-conf-autoref.git origin master`



### Pip

Tests and documentation are not finished yet! So, nope!



## HOW TO USE

Imagine a beautiful JSON files like this:

```json
{
    "project-name":"fantastic-bigdata-project"
    ,"hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/$project-name"
    ,"hdfs-paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
    ,"kafka":{
        "servers":['address1:port1','address2:port2','address3:port3']
        ,"user":"$hdfs-user"
        ,"password":"some-password"
        ,"topics":[
            "topic"
            ,"topic2"
        ]
    }
    ,"download":{
        "tmp-dir":"/mnt/tmp-storage"
        ,"provider1":{
            addresses:[
                "files-address1"
            	,"files-address2"
            ]
            ,hdfs-destiny:"$hdfs-paths.incoming"
        }
    }
}
```



Repare that `hdfs-user` and `hdfs-base`is referenced in some other places in file using the character '$'. 



### Loading config data

```python
import json-conf-autoref

# Loading from file
conf = process(file='default.conf')

# Showing all vars from conf
show(conf)

# Loading from JSON string - Please, don't do that!
conf = process(json_string= """{
    "hdfs-user":"john"
    ,"hdfs-base":"/usr/$hdfs-user/fantastic-bigdata-project"
    ,"paths":{
        "incoming":"$hdfs-base/incoming"
        ,"processing":"$hdfs-base/processing"
        ,"processed":"$hdfs-base/processed"
        ,"rejected":"$hdfs-base/rejected"
    }
    ,"remote-conns":{
        "algorithm":"naive-bayes"
        ,
    }
}""")
               
show(conf)
    
```

Le result:

```

```









### Accessing data



To access data is just any Python data structure.

```
# Common stuff, just like with a simple 
hdfs_user = conf['hdfs-user']

# By "point-paths"
incoming_path = get('paths.incoming')

```



### Setting value



Not supported yet! Yet...



