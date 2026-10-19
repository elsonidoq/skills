"""T002/V4 counter-epoch attribution; actual two-turn readings in BindingTests."""
import copy
import unittest
from coherence_workflow.pi_adapter import usage_segment, non_agent_segment


class UsageSegmentsTests(unittest.TestCase):
    def sample(self):
        return dict(session_id='s',branch='b',epoch='e',counters=dict(input=10,output=5,cacheRead=0,cacheWrite=0),cost=.1,occupancy=100)

    def test_zero_is_data_and_context_not_billing(self):
        before=self.sample();after=self.sample();after['counters']['input']=15;after['occupancy']=999
        segment=usage_segment(before,after)
        self.assertEqual(segment['tokens']['input']['value'],5)
        self.assertEqual(segment['tokens']['cacheRead'],{'value':0,'unknown_reason':None})
        self.assertEqual(segment['tokens']['cacheWrite']['value'],0)
        self.assertEqual(segment['cost']['value'],0)

    def test_reopen_branch_reset_missing_and_death(self):
        for key,value in [('session_id','different'),('branch','fork'),('epoch','reopen')]:
            after=self.sample();after[key]=value
            self.assertIsNone(usage_segment(self.sample(),after)['tokens']['input']['value'])
        after=self.sample();after['counters']['input']=0
        self.assertEqual(usage_segment(self.sample(),after)['tokens']['input']['unknown_reason'],'counter_reset')
        for before,after,kwargs in [(None,self.sample(),{}),(self.sample(),None,{}),
                 (self.sample(),self.sample(),{'exclusive':False}),
                 (self.sample(),self.sample(),{'outcome':'ambiguous_summary'})]:
            segment=usage_segment(before,after,**kwargs)
            self.assertTrue(all(v['value'] is None and v['unknown_reason'] for v in segment['tokens'].values()))
            self.assertIsNone(segment['cost']['value'])

    def test_missing_counter_independent_fields_and_no_fake_agent(self):
        after=self.sample();after['counters'].pop('cacheRead')
        segment=usage_segment(self.sample(),after)
        self.assertIsNone(segment['tokens']['cacheRead']['value'])
        self.assertEqual(segment['tokens']['output']['value'],0)
        for kind in ['code','gate','terminal']:
            self.assertIsNone(non_agent_segment(kind)['session_id'])
            self.assertIsNone(non_agent_segment(kind)['tokens'])


class RepairMetricsTests(unittest.TestCase):
    def test_runner_repair_count_is_explicit_and_revision_is_not_added_twice(self):
        from coherence_workflow.projections import metric_record, latest_metrics
        from coherence_workflow.registry import validate_schema
        event={'run_id':'fixture','seq':1,'event_id':'one'}
        operation={'kind':'sdk-turn','node_id':'repair','op_id':'actual-logical-fixture'}
        segment={'role':'repair','task_id':'original','attempt_id':'correction:2','outcome':'settled',
                 'selection':{'reason':'fresh_only','repair_count':2},'before':{},'after':{},
                 'tokens':{key:{'value':0,'unknown_reason':None} for key in ('input','output','cacheRead','cacheWrite')}}
        first=metric_record(event,operation,segment);validate_schema('projection.schema.json',first)
        self.assertEqual(first['payload']['repair_count'],2)
        self.assertEqual(first['payload']['cache_read_tokens']['value'],0)
        self.assertIsNone(first['payload']['context_end']['value'])
        second=metric_record({**event,'seq':2,'event_id':'two'},operation,{**segment,'result_sha':'fixture-committed-head'})
        second['payload']['supersedes']=first['record_id'];validate_schema('projection.schema.json',second)
        current=latest_metrics([first,second]);self.assertEqual(len(current),1)
        self.assertEqual(current[0]['payload']['repair_count'],2)

    def test_nonagent_metric_keeps_profile_session_tokens_null(self):
        from coherence_workflow.projections import metric_record
        from coherence_workflow.registry import validate_schema
        record=metric_record({'run_id':'fixture','seq':1,'event_id':'code'},
                             {'kind':'graph','node_id':'verify','op_id':'code-operation'}, {'outcome':'ok'})
        validate_schema('projection.schema.json',record)
        for field in ('session_id','requested_profile','observed_runtime','skill_requested','reused'):
            self.assertIsNone(record['payload'][field])
        self.assertIsNone(record['payload']['input_tokens']['value'])
        self.assertEqual(record['payload']['input_tokens']['unknown_reason'],'non_agent_node')

    def test_checkpoint_metric_ids_are_unique_for_multiple_attempts_of_one_task(self):
        import tempfile
        from pathlib import Path
        from coherence_workflow.projections import records, latest_metrics
        from coherence_workflow.store import Authority, digest
        from fixtures.support import make_project
        with tempfile.TemporaryDirectory() as temp:
            project=make_project(Path(temp)/'project')
            with Authority(project) as owner:
                store=owner.store;store.reserve('run',digest('fixture'))
                store.db.execute('CREATE TABLE wf_checks(evidence_id TEXT,run_id TEXT,task_id TEXT)')
                for count,role in enumerate(('implement','repair')):
                    segment={'task_id':'same-task','attempt_id':'same-task:'+str(count),'role':role,'outcome':'settled',
                             'before':{},'after':{},'selection':{'reason':'fixture-only','repair_count':count},'tokens':{}}
                    op=store.intent('run','attempt:'+str(count),'sdk-turn',{},{});store.transition(op['op_id'],'intent','completed',segment)
                with store.transaction() as db:store.event(db,'run',None,'task_checkpointed',{'task_id':'same-task','sha':'fixture-head'})
                _,metrics=records(store.db,'run')
                self.assertEqual(len(metrics),4)
                self.assertEqual(len({r['record_id'] for r in metrics}),4)
                current=latest_metrics(metrics);self.assertEqual(len(current),2)
                self.assertEqual({r['payload']['role'] for r in current},{'implement','repair'})

    def test_later_evidence_does_not_rewrite_checkpoint_metric_history(self):
        import tempfile
        from pathlib import Path
        from coherence_workflow.projections import records
        from coherence_workflow.store import Authority, canonical, digest
        from fixtures.support import make_project
        with tempfile.TemporaryDirectory() as temp:
            project=make_project(Path(temp)/'project')
            with Authority(project) as owner:
                store=owner.store;store.reserve('run',digest('fixture'))
                store.db.execute('CREATE TABLE wf_checks(evidence_id TEXT,run_id TEXT,task_id TEXT)')
                segment={'task_id':'A','attempt_id':'A:0','role':'implement','outcome':'settled','before':{},'after':{},'selection':{'reason':'fixture-only'},'tokens':{}}
                op=store.intent('run','attempt','sdk-turn',{},{});store.transition(op['op_id'],'intent','completed',segment)
                with store.transaction() as db:
                    db.execute('INSERT INTO wf_checks VALUES(?,?,?)',('before','run','A'))
                    store.event(db,'run',None,'check_observed',{'evidence_id':'before'})
                    store.event(db,'run',None,'task_checkpointed',{'task_id':'A','sha':'fixture-head'})
                original=records(store.db,'run')[1]
                self.assertEqual(original[-1]['payload']['evidence_refs'],['before'])
                with store.transaction() as db:
                    db.execute('INSERT INTO wf_checks VALUES(?,?,?)',('after','run','A'))
                    store.event(db,'run',None,'check_observed',{'evidence_id':'after'})
                self.assertEqual(canonical(original),canonical(records(store.db,'run')[1]))
