// Offline installation-layout tests. No provider, install, or host transport.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import test from 'node:test';
import {discoverSdk, resolvePackage} from '../pi-host/sdk-resolution.mjs';

const sdkName = '@earendil-works/pi-coding-agent';
const dependency = '@earendil-works/pi-ai';

async function packageAt(directory, name, value) {
  await fs.mkdir(path.join(directory, 'public'), {recursive: true});
  // Import-only exports and a deliberately non-dist entry catch both physical
  // path assumptions and accidental CommonJS resolution.
  await fs.writeFile(path.join(directory, 'package.json'), JSON.stringify({
    name, type: 'module', exports: {'.': {import: './public/entry.mjs'}},
  }));
  await fs.writeFile(path.join(directory, 'public/entry.mjs'), `export const marker = ${JSON.stringify(value)};`);
  return directory;
}

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'sdk-resolution-'));
  t.after(() => fs.rm(root, {recursive: true, force: true}));
  const hostURL = pathToFileURL(path.join(root, 'checkout/runtime/pi-host/sdk.mjs'));
  return {root, hostURL, home: path.join(root, 'home'), env: {}};
}

for (const layout of ['nested', 'hoisted', 'symlinked']) {
  test(`local SDK public exports and ${layout} dependency resolve to the SDK instance`, async t => {
    const options = await fixture(t);
    const hostDir = path.dirname(fileURLToPath(options.hostURL));
    const sdkDir = await packageAt(path.join(hostDir, 'node_modules', sdkName), sdkName, 'sdk');
    const dependencyDir = layout === 'nested'
      ? path.join(sdkDir, 'node_modules', dependency)
      : layout === 'hoisted'
        ? path.join(hostDir, 'node_modules', dependency)
        : path.join(options.root, 'linked-dependency');
    await packageAt(dependencyDir, dependency, layout);
    if (layout === 'symlinked') {
      const link = path.join(hostDir, 'node_modules', dependency);
      await fs.mkdir(path.dirname(link), {recursive: true});
      await fs.symlink(dependencyDir, link);
    }
    const discovered = discoverSdk(options);
    assert.equal(discovered.packageDir, sdkDir);
    assert.equal((await import(discovered.entryURL)).marker, 'sdk');
    const entry = resolvePackage(dependency, discovered.entryURL);
    assert.equal((await import(entry)).marker, layout);
  });
}

test('SDK selection preserves local then explicit precedence', async t => {
  const options = await fixture(t);
  const local = path.join(path.dirname(fileURLToPath(options.hostURL)), 'node_modules', sdkName);
  await packageAt(local, sdkName, 'local');
  const explicit = await packageAt(path.join(options.root, 'explicit'), sdkName, 'explicit');
  options.env.PI_PACKAGE_DIR = explicit;
  assert.equal((await import(discoverSdk(options).entryURL)).marker, 'local');
  await fs.rm(local, {recursive: true});
  assert.equal((await import(discoverSdk(options).entryURL)).marker, 'explicit');
});

test('resolver never executes caller NODE_OPTIONS preloads', async t => {
  const options = await fixture(t);
  const directory = await packageAt(path.join(options.root, 'sdk'), sdkName, 'safe');
  const preload = path.join(options.root, 'preload.mjs');
  await fs.writeFile(preload, 'throw new Error("workflow preload must not run in resolver");');
  const previous = process.env.NODE_OPTIONS;
  try {
    process.env.NODE_OPTIONS = '--import=' + pathToFileURL(preload).href;
    assert.match(discoverSdk({...options, env: {PI_PACKAGE_DIR: directory}}).entryURL, /public\/entry.mjs$/);
  } finally {
    if (previous === undefined) delete process.env.NODE_OPTIONS;
    else process.env.NODE_OPTIONS = previous;
  }
});

test('explicit SDK directory supports a symlinked package without dist assumptions', async t => {
  const options = await fixture(t);
  const real = await packageAt(path.join(options.root, 'actual-sdk'), sdkName, 'explicit');
  const link = path.join(options.root, 'selected-sdk');
  await fs.symlink(real, link);
  const discovered = discoverSdk({...options, env: {PI_PACKAGE_DIR: link}});
  assert.equal((await import(discovered.entryURL)).marker, 'explicit');
  await packageAt(path.join(real, 'node_modules', dependency), dependency, 'sdk dependency');
  // Resolve from the real SDK entry, as SDK imports do, not its external link.
  const entry = resolvePackage(dependency, discovered.entryURL);
  assert.equal((await import(entry)).marker, 'sdk dependency');
});

for (const custom of [false, true]) {
  test(`${custom ? 'configured' : 'default'} Pi installation follows current-version after updates`, async t => {
    const options = await fixture(t);
    const agent = custom ? path.join(options.root, 'custom-agent') : path.join(options.home, '.pi/agent');
    if (custom) options.env.PI_CODING_AGENT_DIR = agent;
    for (const version of ['before-update', 'after-update']) {
      await packageAt(path.join(agent, 'install/releases', version, 'node_modules', sdkName), sdkName, version);
      await fs.writeFile(path.join(agent, 'install/current-version'), version + '\n');
      const discovered = discoverSdk(options);
      assert.equal((await import(discovered.entryURL)).marker, version);
    }
  });
}

test('discovery does not execute package code and preserves actual import errors', async t => {
  const options = await fixture(t);
  const directory = await packageAt(path.join(options.root, 'sdk'), sdkName, 'unused');
  await fs.writeFile(path.join(directory, 'public/entry.mjs'), 'throw new Error("actual SDK failure");');
  const discovered = discoverSdk({...options, env: {PI_PACKAGE_DIR: directory}});
  await assert.rejects(import(discovered.entryURL), /actual SDK failure/);
});

test('missing SDK and invalid explicit selection have actionable errors', async t => {
  const options = await fixture(t);
  assert.throws(() => discoverSdk(options), /Pi SDK unavailable.*PI_PACKAGE_DIR/);
  assert.throws(() => discoverSdk({...options, env: {PI_PACKAGE_DIR: path.join(options.root, 'absent')}}),
    /Cannot resolve the Pi SDK public entry.*correct PI_PACKAGE_DIR/);
});
