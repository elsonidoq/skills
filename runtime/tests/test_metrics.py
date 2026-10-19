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
