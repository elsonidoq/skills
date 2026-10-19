"""Registered real test-tool capability and its closed argument contract."""
from pathlib import Path
import sys
from coherence_workflow.tools import ProcessTool


def process_tool(project):
    script=Path(__file__).with_name('task_tool.py').resolve()
    return ProcessTool('fixture','1',{
        'type':'object','additionalProperties':False,
        'properties':{'mode':{'enum':['quick','hang','survivor','survivor_hang']},'exit':{'enum':[0,1]}},
        'required':['mode','exit']},
        lambda args:[str(Path(sys.executable).resolve()),str(script),args['mode'],str(project/'owned.txt'),str(args['exit'])],
        ('owned.txt',),{'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'})
