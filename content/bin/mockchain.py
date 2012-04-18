#!/usr/bin/python -tt
# by skvidal
# gplv2+
# copyright 2012 Red Hat, Inc.
# mockchain
# take a mock config and a series of srpms
# rebuild them one at a time
# adding each to a local repo
# so they are available as build deps to next pkg being built

import sys
import subprocess
import os
import optparse
import tempfile
import shutil
import yum


mockconfig_path='/etc/mock'

def createrepo(path):
    cmd = subprocess.Popen(['/usr/bin/createrepo', path],
             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = cmd.communicate()
    return out, err

def parse_args(args):
    parser = optparse.OptionParser('mockchain mockcfg pkg1 [pkg2] [pkg3]')
    parser.add_option('-l', '--localrepo', default=None, 
            help="local path for the local repo, defaults to making its own")
    parser.add_option('-c', '--continue', default=False, action='store_true',
            dest='cont',
            help="if a pkg fails to build, continue to the next one")
    parser.add_option('-a','--addrepo', default=[], action='append',
            dest='repos',
            help="add these repo baseurls to the chroot's yum config")

    #FIXME?
    # figure out how to pass other args to mock?
    opts, args = parser.parse_args(args)
    if len(sys.argv) < 3:
        print "mock-chain mockcfg pkg1 pkg2 pkg3"
        sys.exit(1)


    return opts, args
    
def add_local_repo(infile, destfile, baseurl, repoid=None):
    """take a mock chroot config and add a repo to it's yum.conf
       infile = mock chroot config file
       destfile = where to save out the result
       baseurl = baseurl of repo you wish to add"""
        
    try:
        config_opts = {}
        execfile(infile)
        if not repoid:
            repoid=baseurl.split('//')[1].replace('/',',')
        localyumrepo="""
[%s]
name=%s
baseurl=%s
enabled=1
skip_if_unavailable=1
cost=1
""" % (repoid, baseurl, baseurl)

        config_opts['yum.conf'] += localyumrepo
        br_dest = open(destfile, 'w')
        for k,v in config_opts.items():
            br_dest.write("config_opts[%r] = %r\n" % (k, v))
        br_dest.close()
        return True
    except (IOError, OSError), e:
        print("Could not write mock config to %s" % destfile)
        return False

    return True

def main(args):
    opts, args = parse_args(args)
    # take mock config + list of pkgs
    cfg=args[1]
    pkgs=args[2:]
    mockcfg = mockconfig_path + '/' + cfg + '.cfg'
   
    if not os.path.exists(mockcfg):
        print "could not find config: %s" % mockcfg
        sys.exit(1)

    # create a tempdir for our local info
    if opts.localrepo:
        local_tmp_dir = opts.localrepo
        if not os.path.exists(local_tmp_dir):
            os.makedirs(local_tmp_dir)
    else:            
        pre = 'mock-chain-%s-' % os.getlogin()
        local_tmp_dir = tempfile.mkdtemp(prefix=pre)

    os.chmod(local_tmp_dir, 0755)

    local_repo_dir = os.path.normpath(local_tmp_dir + '/results/')
    if not os.path.exists(local_repo_dir):
        os.makedirs(local_repo_dir, mode=0755)
            
    local_baseurl="file://%s" % local_repo_dir
    print "files will be written to: %s" % local_repo_dir
    config_path = os.path.normpath(local_tmp_dir + '/configs/')
    if not os.path.exists(config_path):
        os.makedirs(config_path, mode=0755)

    print "config files for mock into: %s" % config_path

    my_mock_config = config_path + '/' + os.path.basename(mockcfg)
    # modify with localrepo
    if not  add_local_repo(mockcfg, my_mock_config, local_baseurl, 'local_build_repo'):
         print "Could not write out local config"
         sys.exit(1)

    for baseurl in opts.repos:
         if not add_local_repo(my_mock_config, my_mock_config, baseurl):
            print "Could not add: %s to yum config in mock chroot" % baseurl
            sys.exit(1)

        
    # these files needed from the mock.config dir to make mock run
    for fn in ['site-defaults.cfg', 'logging.ini']:
        pth = mockconfig_path + '/' + fn
        shutil.copyfile(pth, config_path + '/' + fn)

   
    # createrepo on it
    out, err = createrepo(local_repo_dir)
    if err.strip():
        print "Error making local repo: %s" % local_repo_dir
        print "Err: %s" % err
        sys.exit(1)

# for pkg in pkgs:
  # build pkg
  # copy results to that path
  # createrepo on it
  # if any fail to build, abort and complain
    built_pkgs = []
    for pkg in pkgs:
        print " * Processing:", pkg
        s_pkg = os.path.basename(pkg)
        pobj = yum.packages.YumLocalPackage(filename=pkg)
        resdir = '%s/%s/%s-%s-%s' % (local_repo_dir, cfg, pobj.name,
                                pobj.version, pobj.release)
        resdir = os.path.normpath(resdir)
        if not os.path.exists(local_repo_dir):
            os.makedirs(resdir)

        success_file = resdir + '/success'
        if os.path.exists(success_file):
            print 'skipping %s - already built' % s_pkg
            continue

        print 'building %s' % s_pkg
        args = ['/usr/bin/mock',
           '--configdir', config_path,
           '--resultdir', resdir,
#               '--no-clean-after',
           '-r', cfg, pkg,
        ]
        print "Running:", " ".join(args)
        cmd = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, err = cmd.communicate()
        if cmd.returncode != 0:
            print "Error building: %s" % s_pkg
            print "See results in: %s" % resdir
            if not opts.cont:
                sys.exit(1)
        else:
            open(success_file, 'w').write('done\n')
            built_pkgs.append(s_pkg)
            # createrepo with the new pkgs
            out, err = createrepo(local_repo_dir)
            if err.strip():
                print "Error making local repo: %s" % local_repo_dir
                print "Err: %s" % err
                sys.exit(1)
        print " * Done with:", pkg


    print "Results out to: %s" % local_repo_dir
    print "Pkgs built: %s" % len(built_pkgs)
    print '\n'.join(built_pkgs)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
