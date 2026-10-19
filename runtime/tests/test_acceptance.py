"""T010: actual docs/schema/help, bounded evidence applicability, external review barrier.

The parent owns independent-review provenance. These checks reject absent/stale/incomplete
receipts; a self-authored fixture cannot supply the actual independent review/manual gate.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'.pi/workflow-validation/implementation/t010'
MIGRATION_BASE='75353862f79e97da941057accdcaa921fc9cf31f'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def candidate_files():
    # This migration's final task owns documentation/tests only. Preserve unrelated state.
    owned=['docs/coordinate-implementation.md','docs/coordinate-implementation-schema.md','docs/index.md',
           'README.md','REQUIREMENTS.md','AGENTS.md','docs/plans/planner-regression.md','docs/pi-settings-sample.md',
           'runtime/tests/test_acceptance.py','runtime/tests/test_migration.py','scripts/check-skills-lint.sh']
    return {p:sha(ROOT/p) for p in owned if (ROOT/p).is_file()}


def git_boundary_errors(text):
    body=text.split('## Storage, launch and failure rules',1)[-1].split('## Containment',1)[0]
    return ['stale current Git boundary: '+phrase for phrase in
            ('Git commits/recovery are not implemented here','Future commits') if phrase in body]


class DocumentationAcceptanceTests(unittest.TestCase):
    def test_current_storage_section_never_denies_delivered_git_checkpoint_and_recovery(self):
        text=(ROOT/'docs/coordinate-implementation.md').read_text()
        self.assertEqual(git_boundary_errors(text),[])
        self.assertIn('Runner Git checkpoints and exact existing-commit recovery are implemented',text)
        self.assertIn('Signing/hooks remain enabled and scoped',text)

    def test_actual_help_flags_and_portable_resource_docs(self):
        text=(ROOT/'docs/coordinate-implementation.md').read_text()
        for command in ('start','resume','intake','status','pending','answer','control','parent-ready','parent-received','parent-answer'):
            result=subprocess.run([sys.executable,'-m','coherence_workflow.cli',command,'--help'],
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn(command,text)
            for flag in set(re.findall(r'--[a-z][a-z-]*',result.stdout))-{'--help'}:
                self.assertIn(flag,text,(command,flag))
        for phrase in ('--suite-root','share/coherence-workflow/pi-host','explicit','Host exit',
                       'not a filesystem sandbox','/reload','legacy','rollback','no automatic'):
            self.assertIn(phrase,text)
        for stale in ('first-session independence still requires the future','Rollout remains opt-in',
                      'registry entries remain unavailable until','interactive parent transport remains gated\nuntil its separately verified adapter is delivered'):
            self.assertNotIn(stale,text)

    def test_published_schema_fields_and_current_sql_owner(self):
        text=(ROOT/'docs/coordinate-implementation-schema.md').read_text()
        projection=json.loads((ROOT/'runtime/coherence_workflow/schemas/projection.schema.json').read_text())
        for branch in projection['oneOf']:
            for field in branch['properties']:
                self.assertIn('`'+field+'`',text)
            for field in branch['properties']['payload']['properties']:
                self.assertIn('`'+field+'`',text)
        for phrase in ('schema version 1','BEGIN IMMEDIATE','WAL','FULL','separate connection/transaction',
                       'null','unknown','supersedes','not exactly-once','execution_intent'):
            self.assertIn(phrase,text)
        for stale in ('Projections are not published','No wf_tasks/sessions/checks/gates/outbox tables exist',
                      'complete planned runtime','intake later','publisher later'):
            self.assertNotIn(stale,text)

    def test_current_routing_links_and_preservation_boundaries(self):
        for name in ('README.md','REQUIREMENTS.md','AGENTS.md','docs/index.md',
                     'docs/coordinate-implementation.md','docs/coordinate-implementation-schema.md'):
            text=(ROOT/name).read_text()
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if target.startswith(('http','#')) or '<' in target:continue
                self.assertTrue((ROOT/name).parent.joinpath(target.split('#',1)[0]).exists(),(name,target))
        operating=(ROOT/'docs/coordinate-implementation.md').read_text()
        for phrase in ('sqlite','Pi','partial','commits','unrelated','drain','reconciliation',
                       'No DB downgrade','never automatically restart legacy','GHSA-qhr7-859c-m2p7'):
            self.assertIn(phrase.lower(),operating.lower())


class FullRangeAcceptanceTests(unittest.TestCase):
    def test_current_item_proof_all_requirements_and_design_checks(self):
        evidence=json.loads((PROOF/'evidence.json').read_text())
        tasks=json.loads((ROOT/'specs/003-coordinate-workflow/tasks.json').read_text())['tasks']
        expected={item['id'] for task in tasks for item in task['required']}
        self.assertEqual(set(evidence['items']),expected)
        for task in tasks:
            for gate in task['gates']:
                self.assertEqual(evidence['gates'][gate['id']]['status'],'fulfilled',gate['id'])
            for item in task['required']:
                record=evidence['items'][item['id']]
                self.assertEqual(record['status'],'satisfied',item['id'])
                self.assertEqual(record['criterion_sha256'],hashlib.sha256(json.dumps(item,sort_keys=True,separators=(',',':')).encode()).hexdigest())
                self.assertGreater(record['collected'],0,item['id']);self.assertEqual(record['exit_code'],0,item['id'])
                self.assertTrue(record['command'] and record['applicability'] and record['environment'])
                for path,digest in record['outputs'].items():
                    file=ROOT/path;self.assertGreater(file.stat().st_size,0,path);self.assertEqual(sha(file),digest,path)
        self.assertEqual(set(evidence['requirements']),{f'FR-{i:03d}' for i in range(1,41)})
        self.assertEqual(set(evidence['success_criteria']),{f'SC-{i:03d}' for i in range(1,10)})
        self.assertEqual(set(evidence['design_checks']),{'V-config','V-intake','V-binding','V-session','V-metrics',
            'V-recovery','V-custody','V-evidence','V-review','V-status','V-authority','V-interaction','V-control','V-migration'})
        for record in [*evidence['requirements'].values(),*evidence['success_criteria'].values(),*evidence['design_checks'].values()]:
            self.assertTrue(record['source_mapping']);self.assertTrue(record['items']);self.assertTrue(set(record['items'])<=expected)
        print('current proof union:',len(expected),'REQUIRED; FR001–040, SC001–009, 14 design checks; actual output hashes verified')

    def test_actual_independent_full_range_review_current_candidate_or_confirmed_head(self):
        path=Path(os.environ.get('COHERENCE_FULL_RANGE_REVIEW',str(PROOF/'independent-review.json')))
        self.assertTrue(path.is_file(),'fresh independent full-range review UNAVAILABLE; parent must supply actual review, no self-certification')
        receipt=json.loads(path.read_text())
        self.assertEqual(receipt['range_base'],MIGRATION_BASE)
        self.assertEqual(receipt['candidate_files'],candidate_files(),'reviewed candidate bytes changed')
        report=Path(receipt['report_path']);self.assertGreater(report.stat().st_size,0)
        self.assertEqual(sha(report),receipt['report_sha256'])
        self.assertEqual(receipt['verdict'],'pass')
        self.assertTrue(receipt['reviewer_session'] and receipt['parent_verified_provenance'])
        self.assertEqual(receipt['unresolved_findings'],[])
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        self.assertEqual(head,receipt.get('final_head') or receipt['reviewed_head'])
        subprocess.run(['git','merge-base','--is-ancestor',MIGRATION_BASE,head],cwd=ROOT,check=True)
        if receipt.get('final_head'):
            tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
            self.assertEqual(tree,receipt['candidate_tree'])
        print('actual independent review artifact and current range/candidate checked:',MIGRATION_BASE,head)
