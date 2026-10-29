// Discovery only: never import the SDK or start workflow transport here.
import {execFileSync} from 'node:child_process';
import {existsSync, readFileSync} from 'node:fs';
import {findPackageJSON} from 'node:module';
import {homedir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const SDK_PACKAGE = '@earendil-works/pi-coding-agent';

// NODE_OPTIONS uses double-quoted strings and backslash escapes inside quotes.
// Keep only resolution settings, not --import/--require or executable loaders.
function resolutionOptions() {
  const environment = [];
  let word = '', quoted = false, escaped = false;
  for (const char of process.env.NODE_OPTIONS || '') {
    if (escaped) { word += char; escaped = false; }
    else if (quoted && char === '\\') escaped = true;
    else if (char === '"') quoted = !quoted;
    else if (/\s/.test(char) && !quoted) {
      if (word) environment.push(word);
      word = '';
    } else word += char;
  }
  if (word) environment.push(word);
  const args = [...environment, ...process.execArgv];
  const selected = [];
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (/^--(?:no-)?(?:preserve-symlinks(?:-main)?|addons|experimental-require-module)$/.test(arg)) {
      selected.push(arg);
    } else if (arg === '--conditions' || arg === '-C') {
      selected.push(arg, args[++i]);
    } else if (arg.startsWith('--conditions=') || arg.startsWith('-C=')) selected.push(arg);
  }
  return selected;
}

// Node's parent-aware ESM resolver is flag-gated. Keep the flag in a short-lived
// resolver process rather than requiring flags on Pi, Paseo, or every test.
// Resolution honors package exports (including import-only exports), hoisting,
// and symlinks; no package code is executed by this process.
export function resolvePackage(specifier, parentURL) {
  return execFileSync(process.execPath, [
    ...resolutionOptions(), '--experimental-import-meta-resolve', '--input-type=module', '-e',
    'process.stdout.write(import.meta.resolve(process.argv[1], process.argv[2]))',
    specifier, String(parentURL),
  ], {encoding: 'utf8', env: {...process.env, NODE_OPTIONS: ''}, stdio: ['ignore', 'pipe', 'pipe']}).trim();
}

function installedPackage(parentURL) {
  try {
    return findPackageJSON(SDK_PACKAGE, parentURL);
  } catch (error) {
    if (error.code === 'ERR_MODULE_NOT_FOUND') return undefined;
    throw error;
  }
}

export function discoverSdk({hostURL = import.meta.url, env = process.env, home = homedir()} = {}) {
  let packageFile = installedPackage(hostURL);
  if (!packageFile && env.PI_PACKAGE_DIR) {
    packageFile = path.join(env.PI_PACKAGE_DIR, 'package.json');
  }
  if (!packageFile) {
    for (const agentDir of new Set([env.PI_CODING_AGENT_DIR, path.join(home, '.pi', 'agent')].filter(Boolean))) {
      const versionFile = path.join(agentDir, 'install', 'current-version');
      if (!existsSync(versionFile)) continue;
      const version = readFileSync(versionFile, 'utf8').trim();
      if (!version) continue;
      const releaseURL = pathToFileURL(path.join(agentDir, 'install', 'releases', version, 'package.json'));
      packageFile = installedPackage(releaseURL);
      if (packageFile) break;
    }
  }
  if (!packageFile) {
    throw new Error(`Pi SDK unavailable for workflow loading: set PI_PACKAGE_DIR to the installed ${SDK_PACKAGE} package directory, or use the explicit isolated workflow setup.`);
  }
  const packageDir = path.dirname(packageFile);
  try {
    const metadata = JSON.parse(readFileSync(packageFile, 'utf8'));
    if (metadata.name !== SDK_PACKAGE) throw new Error(`Expected package ${SDK_PACKAGE}`);
    return {packageDir, entryURL: resolvePackage(SDK_PACKAGE, pathToFileURL(packageFile))};
  } catch (error) {
    throw new Error(`Cannot resolve the Pi SDK public entry from ${packageDir}; correct PI_PACKAGE_DIR or repair that installation. ${error.stderr?.toString().trim() || error.message}`, {cause: error});
  }
}
