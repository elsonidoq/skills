"""T009/V3 actual offline wheel/resource/foreign-project entry, no global install."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]


class PortableInstallationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name)
        source=cls.root/'build-source'
        shutil.copytree(ROOT/'runtime',source,ignore=shutil.ignore_patterns('node_modules','__pycache__','build','*.egg-info'))
        build_deps=ROOT/'.pi/workflow-validation/implementation/t009/build-deps'
        cls.env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PIP_NO_INDEX='1',
            PYTHONPATH=str(build_deps),TMPDIR=str(cls.root))
        result=subprocess.run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation',
            '--wheel-dir',str(cls.root/'dist'),str(source)],env=cls.env,capture_output=True,text=True,timeout=60)
        if result.returncode:raise AssertionError(result.stdout+result.stderr)
        cls.wheel=next((cls.root/'dist').glob('*.whl'));cls.installed=cls.root/'installed'
        result=subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-index',
            '--target',str(cls.installed),str(cls.wheel)],env=cls.env,capture_output=True,text=True,timeout=30)
        if result.returncode:raise AssertionError(result.stdout+result.stderr)
        # Dependencies are the existing read-only venv; source runtime/test imports are excluded.
        dependencies=[p for p in sys.path if 'site-packages' in p]
        cls.env['PYTHONPATH']=os.pathsep.join([str(cls.installed),*dependencies])
        cls.foreign=cls.root/'unrelated';cls.foreign.mkdir()

    def test_wheel_contains_yaml_schemas_host_lock_and_console_entry(self):
        with zipfile.ZipFile(self.wheel) as wheel:
            names=wheel.namelist()
            for suffix in ('coherence_workflow/workflows/coordinate.yaml','coherence_workflow/schemas/task.schema.json',
                           '/pi-host/host.mjs','/pi-host/package.json','/pi-host/package-lock.json'):
                self.assertTrue(any(name.endswith(suffix) for name in names),suffix)
            for path in ('cli.py','pi_adapter.py','intake.py','notifications/paseo.py'):
                self.assertEqual(wheel.read('coherence_workflow/'+path),(ROOT/'runtime/coherence_workflow'/path).read_bytes())
            entry=next(n for n in names if n.endswith('entry_points.txt'))
            self.assertIn('coordinate-implementation = coherence_workflow.cli:main',wheel.read(entry).decode())

    def test_installed_resource_discovery_and_help_from_unrelated_project(self):
        code='''import json
from importlib.resources import files
import coherence_workflow.cli as cli
from coherence_workflow.pi_adapter import host_resource
host=host_resource()
assert host.is_file() and host.with_name('package-lock.json').is_file()
assert files('coherence_workflow').joinpath('workflows/coordinate.yaml').is_file()
print(json.dumps({'module':cli.__file__,'host':str(host)}))
'''
        result=subprocess.run([sys.executable,'-c',code],cwd=self.foreign,env=self.env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        observed=json.loads(result.stdout)
        self.assertTrue(Path(observed['module']).is_relative_to(self.installed))
        self.assertTrue(Path(observed['host']).is_relative_to(self.installed))
        result=subprocess.run([str(self.installed/'bin/coordinate-implementation'),'start','--help'],
            cwd=self.foreign,env=self.env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('--project',result.stdout);self.assertIn('--suite-root',result.stdout)
        self.assertEqual(list(self.foreign.iterdir()),[],'help silently provisions target')
        print('actual wheel foreign-project resource/help:',observed)

    def test_actual_installed_cli_both_origins_have_no_source_import(self):
        from fixtures.support import make_project
        from test_intake import approved_fixture
        from coherence_workflow.store import digest
        project=make_project(self.root/'foreign-project-intake')
        for origin in ('TinySpec','Standard'):
            contract,catalog=approved_fixture(project,'config',origin)
            tasks=self.root/'tasks.json';tasks.write_text(json.dumps(contract))
            authority=self.root/'catalog.json';authority.write_text(json.dumps(catalog));authority.chmod(0o600)
            result=subprocess.run([str(self.installed/'bin/coordinate-implementation'),'intake',
                '--project',str(project),'--tasks',str(tasks)],
                env=self.env,cwd=project,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)['task_ids'], [task['id'] for task in contract['tasks']])
            print('installed foreign CLI intake',origin,result.returncode)

    def test_explicit_setup_refuses_missing_permission_and_preserves_foreign_prefix(self):
        prefix=self.root/'foreign-prefix';prefix.mkdir();(prefix/'custom').write_text('owner bytes')
        for args in (['--prefix',str(prefix)],['--prefix',str(prefix),'--allow-network']):
            result=subprocess.run([str(ROOT/'scripts/install-workflow.sh'),*args],env=self.env,
                capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertEqual((prefix/'custom').read_text(),'owner bytes')
            self.assertEqual([p.name for p in prefix.iterdir()],['custom'])


class SourceEntryBindingTests(unittest.TestCase):
    def test_foreign_cwd_local_shadow_and_caller_pythonpath_never_replace_source_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);foreign=root/'foreign';foreign.mkdir();conflict=root/'caller';conflict.mkdir()
            marker=root/'shadow-executed'
            for directory in (foreign,conflict):
                package=directory/'coherence_workflow';package.mkdir()
                (package/'__init__.py').write_text('')
                (package/'cli.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("shadow")\nprint("PROJECT_LOCAL_CLI_EXECUTED")\nraise SystemExit(42)\n')
            for path in (None,str(conflict)):
                env=dict(os.environ,COHERENCE_PYTHON=sys.executable);env.pop('PYTHONPATH',None)
                if path:env['PYTHONPATH']=path
                result=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'status','--help'],
                    cwd=foreign,env=env,capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertIn('--project',result.stdout);self.assertNotIn('PROJECT_LOCAL_CLI_EXECUTED',result.stdout)
                self.assertFalse(marker.exists())
