"""Execute the supplied SELECT or CONSTRUCT query against local RDF modules."""
import argparse
import json
from pathlib import Path
from fairmm_rdf import load,write


def main():
    parser=argparse.ArgumentParser();parser.add_argument('query',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=load().query(args.query.read_text(encoding='utf-8'))
    if result.type=='CONSTRUCT':text=result.graph.serialize(format='turtle')
    else:text=json.dumps([{str(key):str(value) if value is not None else None for key,value in row.asdict().items()} for row in result],ensure_ascii=False,indent=2)+'\n'
    if args.output:write(args.output,text)
    else:print(text)


if __name__=='__main__':main()
