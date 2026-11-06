// Regenerate only the offline documentation mockup; never build/start the application.
// Usage: node docs/workflow-monitor-mockup-build.mjs [prepared-monitor-node_modules]
import { readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const docs = dirname(fileURLToPath(import.meta.url));
const root = dirname(docs);
const dependencies = resolve(process.argv[2] ?? join(root, 'workflow_monitor/web/node_modules'));
const require = createRequire(join(dependencies, 'esbuild/package.json'));
const { build } = require(join(dependencies, 'esbuild'));
const lock = JSON.parse(await readFile(join(root, 'workflow_monitor/web/package-lock.json'), 'utf8'));
const result = await build({
  absWorkingDir: root,
  entryPoints: [join(docs, 'workflow-monitor-mockup.jsx')],
  nodePaths: [dependencies],
  bundle: true, write: false, outdir: 'mockup-output', format: 'iife',
  jsx: 'automatic', platform: 'browser', target: 'es2022', minify: true,
  define: { 'process.env.NODE_ENV': '"production"' },
  sourcemap: false, legalComments: 'inline', metafile: true,
});

// Keep the licenses of bundled packages, and verify the prepared versions against
// the existing monitor lockfile. No installation or alternate dependency manifest.
const packages = new Map();
for (const input of Object.keys(result.metafile.inputs)) {
  const absolute = resolve(root, input);
  if (!absolute.includes('/node_modules/')) continue;
  let directory = dirname(absolute);
  for (;;) {
    let pkg;
    try { pkg = JSON.parse(await readFile(join(directory, 'package.json'), 'utf8')); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (pkg?.name && pkg?.version) {
      if (lock.packages[`node_modules/${pkg.name}`]?.version !== pkg.version) {
        throw new Error(`Mockup build: ${pkg.name} does not match the monitor lockfile; use matching prepared dependencies.`);
      }
      if (!packages.has(pkg.name)) {
        let license;
        for (const name of ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'license', 'license.md']) {
          try { license = await readFile(join(directory, name), 'utf8'); break; }
          catch (error) { if (error.code !== 'ENOENT') throw error; }
        }
        if (!license) throw new Error(`Mockup build: license for ${pkg.name} unavailable; retain its license before distributing the bundle.`);
        packages.set(pkg.name, `${pkg.name} ${pkg.version}\n${license}`);
      }
      break;
    }
    const parent = dirname(directory);
    if (parent === directory) throw new Error(`Mockup build: cannot identify bundled package for ${input}.`);
    directory = parent;
  }
}
const bundler = require(join(dependencies, 'esbuild/package.json'));
if (lock.packages['node_modules/esbuild'].version !== bundler.version) throw new Error('Mockup build: use the esbuild version in the monitor lockfile.');
const js = result.outputFiles.find(file => file.path.endsWith('.js')).text;
const css = result.outputFiles.find(file => file.path.endsWith('.css')).text;
const licenses = [...packages].sort(([a], [b]) => a.localeCompare(b)).map(([, license]) => license).join('\n\n');
const htmlPath = join(docs, 'workflow-monitor-mockup.html');
let html = await readFile(htmlPath, 'utf8');
function replace(kind, content) {
  const pattern = new RegExp(`<!-- reactflow-${kind}:start -->[\\s\\S]*?<!-- reactflow-${kind}:end -->`, 'g');
  if ([...html.matchAll(pattern)].length !== 1) throw new Error(`Mockup build: restore the single ${kind} generated-block marker pair in the HTML.`);
  html = html.replace(pattern, () => `<!-- reactflow-${kind}:start -->\n${content}\n<!-- reactflow-${kind}:end -->`);
}
replace('css', `<style id="reactflow-engine-styles">${css.replaceAll('</style', '<\\/style')}</style>`);
replace('js', `<script>/*! Bundled dependency licenses\n${licenses.replaceAll('*/', '* /')}\n*/\n${js.replaceAll('</script', '<\\/script')}</script>`);
await writeFile(htmlPath, html);
console.log(`Updated docs/workflow-monitor-mockup.html (${Buffer.byteLength(html)} bytes; ${packages.size} bundled package licenses).`);
