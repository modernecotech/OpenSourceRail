"""Lossless dictionary-encoded section events with portable compressed bytes."""
import gzip
import json
from .provenance import deterministic_gzip

FIELDS=('journey','train','line','heading','from_station','to_station')
NUMBERS=('depart_minute','arrival_minute','distance_m')


def encode_sections(events):
    dictionaries={key:sorted({row[key] for row in events}) for key in FIELDS}
    indices={key:{value:i for i,value in enumerate(values)} for key,values in dictionaries.items()}
    header=dict(schema='osr-section-events/1',columns=[*FIELDS,*NUMBERS],dictionaries=dictionaries)
    lines=[json.dumps(header,sort_keys=True,separators=(',',':'))]
    lines.extend(json.dumps([*(indices[key][row[key]] for key in FIELDS),*(row[key] for key in NUMBERS)],separators=(',',':')) for row in events)
    return deterministic_gzip(('\n'.join(lines)+'\n').encode())


def decode_sections(raw):
    lines=gzip.decompress(raw).splitlines()
    if not lines:return []
    first=json.loads(lines[0])
    if first.get('schema')!='osr-section-events/1':return [json.loads(line) for line in lines]
    if first['columns']!=[*FIELDS,*NUMBERS]:raise ValueError('unknown section trace columns')
    dictionaries=first['dictionaries']
    for key in FIELDS:
        if len(set(dictionaries[key]))!=len(dictionaries[key]):raise ValueError('duplicate trace dictionary identity')
    result=[]
    for line in lines[1:]:
        row=json.loads(line)
        if len(row)!=len(FIELDS)+len(NUMBERS):raise ValueError('section trace row width differs')
        value={}
        for key,index in zip(FIELDS,row):
            if type(index) is not int or not 0<=index<len(dictionaries[key]):raise ValueError('section trace dictionary index is invalid')
            value[key]=dictionaries[key][index]
        value.update(zip(NUMBERS,row[len(FIELDS):]));result.append(value)
    return result
