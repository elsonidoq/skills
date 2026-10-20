#!/usr/bin/env python3
"""Thin executable-entry contract mutations, not model obedience or live certification."""
from pathlib import Path
import re
import unittest

TEXT=(Path(__file__).parents[1]/'SKILL.md').read_text()


def section(text, heading):
    marker='## '+heading
    start=text.find(marker)
    if start<0:return ''
    end=re.search(r'\n## ',text[start+len(marker):])
    body=text[start:] if end is None else text[start:start+len(marker)+end.start()]
    return ' '.join(body.split())


GUARDS={
    'Load and Verify':('current-content review/scope authorization','Missing, stale or unverifiable approval',
        'TinySpec needs separate source/tasks and combined approval','both current approvals',
        'independent overall review','required SpecKit stage evidence','legacy source shape',
        'Planning-only final approval never launches implementation','technical gotchas',
        'No automatic STATE creation, editing or removal','unrelated dirty work'),
    'Prepare Approved Execution':('No silent provisioning','approved exact implementation/repair bindings',
        'separately from planning/reviewer profiles','unobservable actual binding/effort is unknown',
        'no financial approval/cap/reservation','Separately chargeable API/service actions',
        'explicit scoped authority','no silent manual-polling fallback'),
    'Interface Actions':('explicit current scoped recovery authority','ORIGINAL saved worker conversation',
        'never fresh-session substitution','actually invoke registered ask_user',
        'Received, queued, SDK-delivered','worker-created approved file'),
    'Execute and Integrate':('runner establishes baseline HEAD','allowed paths, index/worktree ownership',
        'never adopts or commits unknown work','one focused verified owned-path',
        'checkpoint per implementation/repair task','No-Git fallback','No extra evidence-only checkpoint',
        'optional checks cannot compensate','Only satisfied REQUIRED items and fulfilled original gates release',
        'Representative-sample manual STOP','same original contracts','Unknown cause blocks blind restart',
        'Runner alone reconciles matching checkpoint receipts','no PID-only fallback'),
    'Review and Acceptance':('fresh independent final review','not an implementation session',
        'full committed revision range','Missing reviewer blocks final acceptance','Every finding has a disposition',
        'implementation complete from accepted'),
    'Runner-configured worker role':('Do NOT launch this CLI','stage/commit or manage workflow state',
        'review read-only','request_owner_input','never technical trivia or direct ask_user'),
}


def contract_errors(text):
    errors=[]
    for heading,clauses in GUARDS.items():
        body=section(text,heading)
        errors += [heading+': missing '+c for c in clauses if c not in body]
    for retired in ('Up to three bounded tasks','More than three require delegation','references/batch-routing.md',
                    'explicit batch/profile approval','Always replan approved tasks',
                    'Accept the worker report without inspecting evidence'):
        if retired in text:errors.append('retired execution authority: '+retired)
    return errors


class IntakeContractTests(unittest.TestCase):
    def test_current_thin_entry(self):
        self.assertEqual(contract_errors(TEXT),[])

    def test_lean_entry_and_bounded_delivery_exception(self):
        self.assertIn('explicitly owner-approved instruction-managed delivery exception', TEXT)
        self.assertIn('Optional headroom telemetry is recorded, not a veto', TEXT)
        self.assertIn('Do NOT launch this CLI', TEXT)

    def test_all_safety_and_authority_guards_are_operative(self):
        for heading,clauses in GUARDS.items():
            for clause in clauses:
                changed=' '.join(TEXT.split()).replace(' ## ','\n## ')
                changed=changed.replace(clause,'REMOVED')+'\n## Footer\n'+clause
                self.assertIn(heading+': missing '+clause,contract_errors(changed))

    def test_retired_llm_execution_routing_cannot_return(self):
        for retired in ('Up to three bounded tasks','More than three require delegation',
                        'references/batch-routing.md','explicit batch/profile approval'):
            self.assertTrue(contract_errors(TEXT+'\n'+retired))


if __name__=='__main__':unittest.main(verbosity=2)
