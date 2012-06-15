#!/usr/bin/env python
""" Script for merging, pushing, building, updating, and buildroot-overriding
changes to a package.

Run this after you have made a change, committed and build the master branch.
"""

import argparse
import textwrap

# The pbs module is amazing.
from pbs import git, fedpkg, bodhi, rpmspec, glob

branches = [
    {
        'short': 'f17',
        'long': 'fc17',
    },
    {
        'short': 'el6',
        'long': 'el6',
    },
]


def config():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--user', dest='user',
        help='Your FAS username.')
    parser.add_argument(
        '--type', dest='type',
        help="Type.  (bugfix, enhancement, security)")
    parser.add_argument(
        '--bugs', dest='bugs',
        help="Specify any number of Bugzilla IDs (--bugs=1234,5678)")
    parser.add_argument(
        '--notes', dest='notes',
        help='Update notes')
    parser.add_argument(
        '--duration', dest='duration', type=int, default=7,
        help="Duration of the buildroot override in days.")
    parser.add_argument(
        '--forgive-build', dest='forgive', action='store_true', default=False,
        help="Don't stop the script if a build fails.")

    args = parser.parse_args()

    required_args = ['user', 'type', 'bugs', 'notes']
    for required in required_args:
        if not getattr(args, required):
            parser.print_usage()
            raise ValueError("%r is required." % required)

    return args


def main():
    args = config()
    spec = glob("*.spec")[0]
    nevr = rpmspec(q=spec).split()[0].rsplit('.', 2)[0]
    print "Processing %r" % nevr
    for branch in branches:
        nevra = nevr + '.' + branch['long']
        print "Working on %r, %r" % (branch['short'], nevra)
        print git.checkout(branch['short'])

        # Merge, push, build
        git.merge("master", _fg=True)
        fedpkg.push(_fg=True)
        if args.forgive:
            try:
                fedpkg.build(_fg=True)
            except Exception, e:
                print "*" * 30
                print str(e)
                print "*" * 30
        else:
            fedpkg.build(_fg=True)

        # Submit a new update.
        kwargs = {
            '_fg': True,
            'new': True,
            'user': args.user,
            'type': args.type,
            'notes': args.notes,
        }
        bodhi(nevra, **kwargs)

        # Buildroot override
        kwargs = {
            '_fg': True,
            'user': args.user,
            'buildroot-override': nevra,
            'duration': args.duration,
            'notes': args.notes,
        }
        bodhi(**kwargs)


if __name__ == '__main__':
    main()
