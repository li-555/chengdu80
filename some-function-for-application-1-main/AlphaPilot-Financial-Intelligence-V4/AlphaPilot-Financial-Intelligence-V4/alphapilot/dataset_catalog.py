"""Read competition workbook-extracted metadata; physical datasets must be separately mounted."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

CATALOG_PATH=Path(__file__).resolve().parent.parent/'catalog'/'competition_tables.json'

def table_catalog()->dict:
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))

def describe_table(name:str)->dict:
    data=table_catalog()['tables']
    if name not in data:raise KeyError(f'Unsupported competition table: {name}')
    return data[name]

def validate_source_columns(table_name:str,columns:list[str])->dict:
    expected={f['field'] for f in describe_table(table_name)['fields']}
    provided=set(columns)
    return {'table':table_name,'recognized':sorted(expected&provided),'unrecognized':sorted(provided-expected),
            'missing':sorted(expected-provided)}

def load_operator_csv(table_name:str,path:str,required:list[str]|None=None)->pd.DataFrame:
    """Operator-controlled import, never invoked by generated application directly."""
    describe_table(table_name)
    df=pd.read_csv(path,low_memory=False)
    checked=validate_source_columns(table_name,df.columns.tolist())
    if checked['unrecognized']:
        raise ValueError('Unexpected columns, inspect mapping: '+str(checked['unrecognized']))
    missing=set(required or [])-set(df.columns)
    if missing:raise ValueError(f'Missing required: {sorted(missing)}')
    return df
