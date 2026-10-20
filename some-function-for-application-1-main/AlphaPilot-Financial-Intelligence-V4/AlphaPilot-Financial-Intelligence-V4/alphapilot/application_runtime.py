"""Small declarative, bounded orchestration prototype, NOT the competition Blocks official schema.

Inputs are already authorized objects bound server-side. Exported docs contain no data or secrets.
"""
from __future__ import annotations
import inspect
import json
import re
from .operations import ALLOWED_OPERATIONS,OPERATION_METADATA,run_named_operation

ID=re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$')

def tools_for_ai()->list[dict]:
    """Machine-readable tool cards for an LLM generating only *existing* operations."""
    manifest=[]
    for name,fn in ALLOWED_OPERATIONS.items():
        signature=inspect.signature(fn)
        params=[]
        for p in signature.parameters.values():
            if p.kind not in [p.POSITIONAL_OR_KEYWORD,p.KEYWORD_ONLY]:continue
            params.append({'name':p.name,'required':p.default is inspect.Parameter.empty})
        manifest.append({'name':name,'description':OPERATION_METADATA[name][0],
                         'parameters':params,'schema_status':'prototype-signatures-not-formal-Blocks-spec',
                         'execute_environment':'restricted server operations only'})
    return manifest

def validate_app(app:dict,input_names:list[str])->list[dict]:
    errors=[]
    if not isinstance(app,dict):return [{'path':'$','code':'TYPE','reason':'Document must be an object'}]
    steps=app.get('steps')
    if not isinstance(steps,list) or not 1<=len(steps)<=25:
        return [{'path':'steps','code':'STEPS','reason':'Require 1–25 steps'}]
    available=set(input_names)
    for i,s in enumerate(steps):
        loc=f'steps[{i}]'
        if not isinstance(s,dict):errors.append({'path':loc,'code':'TYPE','reason':'Step must be object'});continue
        sid=s.get('id');op=s.get('operation');args=s.get('arguments')
        if not isinstance(sid,str) or not ID.fullmatch(sid) or sid in available:
            errors.append({'path':loc+'.id','code':'BAD_ID','reason':'ID invalid or duplicate'})
        if op not in ALLOWED_OPERATIONS:
            errors.append({'path':loc+'.operation','code':'NOT_ALLOWED','reason':f'Unknown operation {op}'});continue
        if not isinstance(args,dict):errors.append({'path':loc+'.arguments','code':'TYPE','reason':'args must be object'});continue
        params=inspect.signature(ALLOWED_OPERATIONS[op]).parameters
        for name,value in args.items():
            if name not in params:errors.append({'path':loc+'.arguments.'+name,'code':'UNKNOWN_ARG','reason':'Unexpected parameter'})
            if isinstance(value,dict) and set(value)=={'$ref'} and value['$ref'] not in available:
                errors.append({'path':loc+'.arguments.'+name,'code':'UNBOUND_REF','reason':f'Reference {value["$ref"]} not bound or not yet computed'})
        required=[p.name for p in params.values() if p.default is inspect.Parameter.empty]
        for param in required:
            if param not in args:errors.append({'path':loc+'.arguments.'+param,'code':'MISSING_ARG','reason':'Required argument'})
        if isinstance(sid,str):available.add(sid)
    return errors

def execute_app(app:dict,bound_inputs:dict)->dict:
    errors=validate_app(app,list(bound_inputs))
    if errors:raise ValueError('Invalid app document: '+json.dumps(errors,ensure_ascii=False))
    namespace=dict(bound_inputs)
    for step in app['steps']:
        kwargs={}
        for k,v in step['arguments'].items():
            kwargs[k]=namespace[v['$ref']] if isinstance(v,dict) and set(v)=={'$ref'} else v
        namespace[step['id']]=run_named_operation(step['operation'],**kwargs)
    return {s['id']:namespace[s['id']] for s in app['steps']}
