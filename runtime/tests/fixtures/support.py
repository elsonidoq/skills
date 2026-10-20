"""Shared isolated Git/config fixtures; no live SDK or provider is simulated as real."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from coherence_workflow.registry import Handler, Registry
from coherence_workflow.store import git


def terminal(context):
    return {'outcome':'done'}


def ok(context):
    return {'outcome':'ok'}


def left(context):
    return {'outcome':'left'}


def right(context):
    return {'outcome':'right'}


def make_project(path):
    path.mkdir(parents=True,exist_ok=True)
    git(path,'init','-q')
    git(path,'config','user.name','Fixture')
    git(path,'config','user.email','fixture@invalid')
    git(path,'config','commit.gpgsign','false')
    for name,value in {'owned.txt':'base','other.txt':'other','STATE.md':'custom state','custom.md':'custom',
                       '.gitignore':'.coherence/\n','skill-a.md':'A','skill-b.md':'B','settings.json':'{}'}.items():
        (path/name).write_text(value)
    git(path,'add','--','owned.txt','other.txt','STATE.md','custom.md','.gitignore','skill-a.md','skill-b.md','settings.json')
    git(path,'commit','-qm','baseline')
    return path


def configuration(root):
    registry = Registry()
    registry.handlers = {}
    registry.success_terminals = {'accepted'}
    profile = {'provider':'fixture','model':'not-a-provider-call','effort':'medium',
               'observer_id':'fixture-observer','observer_version':'1'}
    registry.profiles = {'profile-a':profile,'profile-b':dict(profile,model='another-fixture')}
    registry.skills = {}
    for id in ('a','b'):
        path = 'skill-'+id+'.md'
        hash = hashlib.sha256((root/path).read_bytes()).hexdigest()
        registry.skills['skill-'+id] = {'path':path,'sha256':hash,'resource_hash':hash}
    stages = [('intake','code','intake'),('custody','code','custody'),
              ('choose','code','work'),('work-a','agent','work'),('work-b','agent','work'),
              ('verify','code','verification'),('checkpoint','code','checkpoint'),
              ('review','agent','review'),('accepted','terminal','success')]
    nodes = []
    targets = {'intake':{'ok':'custody'},'custody':{'ok':'choose'},
               'choose':{'left':'work-a','right':'work-b'},'work-a':{'ok':'verify'},'work-b':{'ok':'verify'},
               'verify':{'ok':'checkpoint'},'checkpoint':{'ok':'review'},'review':{'ok':'accepted'},'accepted':{}}
    for id,kind,stage in stages:
        outcomes = tuple(targets[id])
        registry.handlers[id] = Handler(id,'1',kind,stage,outcomes,
             terminal if kind=='terminal' else left if id=='choose' else ok)
        node = {'id':id,'handler':id,'handler_version':'1','type':kind,'outcomes':list(outcomes),
                'transitions':targets[id],'side_effects':[]}
        if kind!='terminal': node['max_retries']=0
        if kind=='agent':
            node.update(role='review' if id=='review' else 'implement',profile='profile-a',skill='skill-a',
                        session_policy={'mode':'fresh_only','min_free_tokens_before_compaction':150000,
                                        'reuse_preference':'own_reviewer' if id=='review' else 'same_group'},
                        max_repair_attempts=0,tools=[],permissions=[])
        nodes.append(node)
    config = {'schema_version':1,'workflow_id':'fixture-config-not-a-name-controller','registry_version':'1',
              'start':'intake','nodes':nodes,'profiles':registry.profiles,'skills':registry.skills,
              'defaults':{'max_repair_attempts':2,'min_free_tokens_before_compaction':150000,
                          'monitor_interval_ms':1000,'telemetry_max_age_ms':2000},
              'storage':{'checkpoint':'.coherence/workflow/workflow.sqlite','event_root':'.coherence/workflow/runs'},
              'permissions':[],'tool_capabilities':[],'containment_capability':None,
              'settings_manifest':{'path':'settings.json','sha256':hashlib.sha256((root/'settings.json').read_bytes()).hexdigest()},
              'interaction':{'mode':'standalone','question_transport':None,'parent_binding_ref':None,'question_tool':None}}
    return registry,config
