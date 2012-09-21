This tools supports managing rpm packaging (spec files and patches) from a git tree.

Why is it needed?
=================

The rpm packaging used in Mer and derived products consists of a tarball and some packaging files. These packages need to be change controlled and that is where problems arise.

Currently for Mer Core the raw tarball[1], patches and packaging files are stored in git.

This leads to:

* inefficient storage: git is not designed to store large binaries efficiently
* opacity: files in the tarball cannot be examined without extracting and unpacking
* dissociation: the upstream change history is lost

So clearly the objectives are:

* increase storage efficiency
* reduce opacity
* retain association with upstream

also

* maintain or improve RE efficiency
* obviousness - eg "git checkout master" should have me ready to hack

For a distro/product there are 2 types of package: native and upstream: upstream may contain additional patches, native doesn't. gitpkg is useful for both upstream and native packages and ensures that packaging is kept distinct from the code.

Upstream code is distributed in many 

The tool assumes that OBS is not being used as the primary store for code and packaging.

Notes:

* The tarball uses src/ as the location for git packages unless pristine-tar is in use

What does it do?
================

There are 2 main uses:

 * create tarball, spec and patches for building/uploading to OBS
 * setup existing packages into a suitable git tree

Normal Operation
================

Assuming a working package that needs changing.

Link the git and osc directories: typically go to the osc co directory::

  rm *
  ln -s /path/to/package/.git .git   # (Should this be a local clone?)
  gp_mkpkg

Now do an osc build to prepare the build environment::

  osc build

Work in the git code tree and use local osc build and quickbuild to get the code working::

  git checkout <code branch>

Once all code is correct, tag it and checkout the pkg branch

Edit the _src file to update the tag for the patches and/or the tarball::

Generate the patches files::

  gp_mkpkg

(FIXME: This needs to support --update-spec and --update-yaml)

Now edit the .spec file and update the Version: Release: (and Patches:/%build)

Edit the .changes file
FIXME: suggest some changes by parsing the git log)

Add changes to git packaging branch (some operations may need more care)::

  git add *spec *changes _src

Then commit and push::

  git commit -s
  git push ....

Examples

 acl : upstream tarball
 build : upstream git
 mer-gfx-tests : native git
 rpm : upstream git + autoconf code in released tarball


Using gp_setup
==============

This can be used to simply create a suitable packaging branch or to import existing packaging.

The TLDR answer::

  gp_setup --existing --pristine --base=RELEASE_0_9_7 --pkgdir=/mer/obs/cobs/Project:KDE:Mer_Extras/oprofile --patch-branch=0.9.7

Worked Example: Importing oprofile
==================================

Upstream uses git so we'll use --base to base off it after cloning it::

  git clone git://oprofile.git.sourceforge.net/gitroot/oprofile/oprofile
  cd oprofile

Determine the tag and verify if a pristine-tar should also be used (eg for autogen.sh)

We have some packaging so check it out (in a different window)::

  osc co Project:KDE:Mer_Extras oprofile

so we can use --existing

Looking at the tarball there are changes to the git tree (autogen.sh etc) so we'll use --pristine

The release tag is "RELEASE_0_9_7" so that will be the --base value; we'll also have a patch-branch of 0.9.7 which we can make Mer release tags on if we add patches.

The command then is::

  gp_setup --existing --pristine --base=RELEASE_0_9_7 --pkgdir=/mer/obs/cobs/Project:KDE:Mer_Extras/oprofile --patch-branch=0.9.7


More examples:

Project with an upstream git and some existing packaging::

  git clone upstream
  gp_setup --existing --base=v3.1.7 --pkgdir=/mer/obs/cobs/Mer:Tools:Testing/pciutils/ --patch-branch=v3.1.7-3

Project with an upstream git, a pristine tar and some existing packaging::

  git clone upstream
  gp_setup --existing --pristine --base=v3.1.7 --pkgdir=/mer/obs/cobs/Mer:Tools:Testing/pciutils/ --patch-branch=v3.1.7-3

Project with no upstream git a pristine tar and some existing packaging but no patches ##FIXME##::

  git init
  gp_setup --existing --pristine --unpack=/mer/obs/cobs/home:auke/xdelta

Project with no upstream git a pristine tar and some existing packaging with patches::

  git init
  gp_setup --existing --pristine --unpack=/mer/obs/cobs/Mer:Tools:Testing/tcl --base=
(needs tags for master and for mer-branch --unpack=<tag>)



Git Names and branch layouts
============================

ver is X.Y.Z and is conceptually an upstream version and ideally a tag.

X.Y.Z-R is the mer version/tag


 upstream/master
            upstream or master branch (can be anything - often a specific
	    branch with rc releases eg in rpm or OBS)

 mer-<ver>
            mer branch per upstream release (re-created based on each
	    upstream release).

	    Commits are handled as patches in spec files.

	    If using pristine-tar then the initial commit is the
	    pristine-tar delta and is not applied as a patch - it's
	    simply there to allow development patches apply cleanly to
	    the tarball.

            Tags are made on here to preserve commits and the branch
	    may be re-based if needed (eg if a patch is removed
	    between -1 and -2 releases) Tags here will be of the form
	    mer-X.Y.Z-R

 pkg-mer
            Discrete commit tree holding any packaging.
	    Tags of pkg-mer-X.Y.Z-R


Git support for multiple sources is possible but complex

Suggested Naming For Non-native packages
========================================

The 'upstream' branch will usually be called master but this isn't
very important.

There should be tags on the upstream code repo with a version.  If
there are any local patches or if pristine-tar is being used then
create a branch called mer-<version> based from this tag.
Mer specific patches/commits should be on the mer-<version> branch.

Tags of the form mer-<version>-<release> should be made on the
mer-<version> branch.

In the pkg-mer branch, there should be tags made called
pkg-mer-<version>-<release>. Typically the _src will be
git:<name>:<version tag>:mer-<version-release tag>.

To be explicit mer-<version>-<release> tags should be made against the
code repo even when there has been no change to the code.

Suggested Naming For Native packages
====================================

The main development branch will usually be called master but this
isn't very important.

There should be tags on the main branch with a version.

In the pkg-mer branch, there should be tags made called
pkg-mer-<version>-<release>. Typically the _src will be
git:<name>:<version tag>.


The _src file
=============

This file defines the src needed for building a package.
It supports:

* Single tarball
* Patches
* Multiple tarballs (yes, kinda, see obs-server)

One line:

* git:<tarball>:<commit1>:<commit2>
* pristine-tar:<tarball>:<commit1>:<commit2>
* Future? Blob : if needed, just store the raw file in a commit

 git:<filename>:<commit1>[:<commit2>]
    <filename> is created in the current directory from git archive at <commit1>
    patches for commits from <commit1> to <commit2> are placed in files
    according to git-patch
    Note that the <commit>s can be tags, branches or sha1s - anything git uses.

 pristine-tar:<filename>[:<commit1>:<commit2>] <filename> is extracted
    from pristine-tar <commit1> represents the closest point on the
    upstream branch to the pristine tar. At this point there's a mer
    branch. The first commit is a simple patch of any files added,
    modified or removed to make the released tarball. Subsequent
    patches are Mer's
    Patches for commits from <commit1> to <commit2> are placed in files
    according to git-patch. THE FIRST COMMIT IS SKIPPED as it's
    in the pristine tarball.
    The filename is obtained from pristine-tar checkout

Notes
=====

gitpkg uses git orphan branches. See   http://stackoverflow.com/questions/1384325/in-git-is-there-a-simple-way-of-introducing-an-unrelated-branch-to-a-repository

Sage asked if it was possible to just clone the packaging or source - it is but it's not trivial::

 git init $PKG
 cd $PKG
 git remote add mer-tools ssh://$USER@review.merproject.org:29418/mer-tools/$PKG
 sed -i '/fetch/s/\*/\pkg-mer/g' .git/config
 git fetch mer-tools

