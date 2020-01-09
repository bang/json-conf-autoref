import json
import sys,os,re



def getAllLookups(json_input,path):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if isinstance(v,str) and re.search(r'^.*?(\$.+?)$',v):
                matches = re.search(r'(\$.+?)/.+?$',v) or re.search(r'(\$.+?)$',v)
                if(matches != None):
                    lookupVar = matches.group(1)
                yield { '/'.join([path , k]) : v }
            else:
                yield from getAllLookups(v, '/'.join([path , k]))
    elif isinstance(json_input, list):
        print("list")
        for item in json_input:
            yield from getAllLookups(item)

def checkResult(data):
    Lookups = []
    for _ in getAllLookups(data,''):
        Lookups.append(_);

    check = False
    if len(Lookups) == 0:
        check = True

    return check

def process(data):
    Lookups = []
    for _ in getAllLookups(data,''):
        Lookups.append(_);

    for l in Lookups:
        for rawPath,lookup in l.items():
            Items = re.split(r'/',rawPath)
            # Getting the JSON PATH accessible through Python data structure
            keyPath = ''
            for i in Items:
                if i == '':
                    continue
                keyPath += "['{}']".format(i)

            ## Looking for lookup on JSON
            # Removing char reference
            target = re.sub(r'\$','',lookup)

            # Getting the value of the placeholder(lookup)
            valuePath = ''
            placeholderName = ''
            if re.search('\.',target):
                targetItems = re.split(r'\.',target)
                for i in targetItems:
                    valuePath += "['{}']".format(i)
                    placeholderName += i
            else:
                valuePath = "['{}']".format(target)
                valuePath = re.sub(r'([^\.].+?)\/.+?$',r"\g<1>']",valuePath)

            # Defining all that 're.sub' function neeeds for the replacement
            placeholderName = re.sub(r'(\$[^\/]+)\/.+?$',r"\g<1>",lookup)
            what = re.sub(r'\$','\\\$',placeholderName)
            to = eval("data{}".format(valuePath))
            where = eval("data{}".format(keyPath))
            exec( "data{} = re.sub(r'{}','{}',{})".format(
                                                keyPath
                                                ,what 
                                                ,to
                                                ,"'" + where + "'"
                                            ) )
    return data


def main():
    jsonDataTable = {}
    data = {}
    with open('default.json') as f:
        data = json.load(f)

    print("Start...")
    data = process(data)

    print("End...")

    print(str(json.dumps(data,indent=4)))

if __name__ == '__main__':
    main()









