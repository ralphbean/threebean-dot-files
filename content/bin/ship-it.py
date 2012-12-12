#!/usr/bin/env python
""" Script for merging, pushing, building, updating, and buildroot-overriding
changes to a package.

Run this after you have made a change, committed and build the master branch.
"""

import argparse
import getpass
import os
import sh
import sys
import textwrap


aggregated = ""
passwd = ""

# open stdout in unbuffered mode
sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)


def _handle_stdout(char, stdin):
    global aggregated
    global passwd

    sys.stdout.write(char.encode())

    aggregated += char

    if "Password for ralph: " == aggregated:
        stdin.put(passwd + "\n")
        print "<entered>"
        aggregated = ""

    if char == "\n":
        aggregated = ""

io = dict(
    _out=_handle_stdout,
    _out_bufsize=0,
    _tty_in=True,
    #_tty_out=True,
    #_tty_in=True,
    #_in=sys.stdin,
    _err_to_out=True,
)

branches = [
    {
        'short': 'f18',
        'long': 'fc18',
    },
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
        '--bugs', dest='bugs', default=None,
        help="Specify any number of Bugzilla IDs (--bugs=1234,5678)")
    parser.add_argument(
        '--notes', dest='notes',
        help='Update notes')
    parser.add_argument(
        '--duration', dest='duration', type=int, default=7,
        help="Duration of the buildroot override in days.")
    parser.add_argument(
        '--branches', dest='branches', default='f18,f17',
        help="Duration of the buildroot override in days.")
    parser.add_argument(
        '--forgive-build', dest='forgive', action='store_true', default=False,
        help="Don't stop the script if a build fails.")
    parser.add_argument(
        '--skip-build', dest='skip', action='store_true', default=False,
        help="Don't build the package.")

    args = parser.parse_args()

    required_args = ['user', 'type', 'notes']
    for required in required_args:
        if not getattr(args, required):
            parser.print_usage()
            raise ValueError("%r is required." % required)

    return args


def main():
    bodhi_cmds = []
    args = config()
    spec = sh.glob("*.spec")[0]
    nevr = sh.rpmspec(q=spec).split()[0].rsplit('.', 2)[0]
    #passwd = getpass.getpass("Enter password:")
    print "Processing %r" % nevr
    branch_keys = args.branches.split(',')
    for branch_key in branch_keys:
        print "Handling %r" % branch_key
        branch = [b for b in branches if b['short'] == branch_key][0]
        nevra = nevr + '.' + branch['long']
        print "Working on %r, %r" % (branch['short'], nevra)
        p = sh.git.checkout(branch['short'], **io)
        p.wait()

        # Merge, push, build
        p = sh.git.merge("master", **io)
        p.wait()

        p = sh.fedpkg.push(**io)
        p.wait()

        if not args.skip:
            if args.forgive:
                try:
                    p = sh.fedpkg.build(**io)
                    p.wait()
                except Exception, e:
                    print "*" * 30
                    print str(e)
                    print "*" * 30
            else:
                p = sh.fedpkg.build(**io)
                p.wait()

        cmd = "bodhi %s --new --user %s --type %s --notes \"%s\"" % (
            nevra, args.user, args.type, args.notes,
        )

        if args.bugs:
            cmd += " -b %s" % args.bugs

        print cmd
        #foo = raw_input("Create a bodhi update in another window... (continue)")

        bodhi_cmds.append(cmd)

        ## Submit a new update.
        #kwargs = {
        #    'new': True,
        #    'user': args.user,
        #    'type': args.type,
        #    'notes': args.notes,
        #}
        #kwargs.update(io)
        #p = sh.bodhi(nevra, **kwargs)
        #p.wait()


        # Ok.. we don't *really* need a buildroot override.
        ## Buildroot override
        #kwargs = {
        #    'user': args.user,
        #    'buildroot-override': nevra,
        #    'duration': args.duration,
        #    'notes': args.notes,
        #}
        #kwargs.update(io)
        #p = sh.bodhi(**kwargs)
        #p.wait()

    print " && ".join(bodhi_cmds)


if __name__ == '__main__':
    main()
