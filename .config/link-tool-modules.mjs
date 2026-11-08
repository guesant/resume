import { mkdirSync, readdirSync, readFileSync, symlinkSync } from 'node:fs';
import { join, resolve } from 'node:path';

const modules = resolve(process.argv[2]);
const bundles = resolve(process.argv[3]);
const commands = join(modules, '.bin');

mkdirSync(commands, { recursive: true });

for (const bundle of readdirSync(bundles)) {
  const directory = join(bundles, bundle);
  const manifest = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'));

  for (const name of Object.keys(manifest.dependencies)) {
    const source = join(directory, 'node_modules', name);
    const target = join(modules, name);
    const pkg = JSON.parse(readFileSync(join(source, 'package.json'), 'utf8'));

    mkdirSync(resolve(target, '..'), { recursive: true });
    symlinkSync(source, target);

    let bins = pkg.bin ?? {};
    if (typeof pkg.bin === 'string') {
      bins = { [name.split('/').at(-1)]: pkg.bin };
    }

    for (const [command, path] of Object.entries(bins)) {
      symlinkSync(join(source, path), join(commands, command));
    }
  }
}
