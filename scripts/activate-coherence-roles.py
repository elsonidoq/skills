#!/usr/bin/env python3
"""Link the legacy no-op extension; install.sh now installs persistent user roles."""
import argparse
import os
from pathlib import Path


def activate(project):
    project = project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError(f'not a project directory: {project}')
    source = (Path(__file__).resolve().parent.parent / 'roles/coherence-roles.js').resolve(strict=True)
    for directory in (project / '.pi', project / '.pi/extensions'):
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError(f'preserved unsafe or foreign directory: {directory}')
        directory.mkdir(exist_ok=True)
    destination = project / '.pi/extensions/coherence-roles.js'
    if destination.is_symlink() and destination.resolve() == source:
        return destination
    if os.path.lexists(destination):
        raise ValueError(f'preserved conflicting entry: {destination}; resolve it before activation')
    destination.symlink_to(source)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path, help='explicit project directory authorized for activation')
    args = parser.parse_args()
    try:
        link = activate(args.project)
    except (OSError, ValueError) as error:
        parser.exit(1, f'role activation blocked: {error}\n')
    print(f'compatibility extension linked: {link}; run scripts/install.sh for persistent user roles')


if __name__ == '__main__':
    main()
