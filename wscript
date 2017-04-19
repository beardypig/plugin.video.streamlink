import os
import re

BUILD_NUMBER = os.environ.get("TRAVIS_BUILD_NUMBER", 0)
APPNAME = "plugin.video.streamlink"
out = "build"
STREAMLINK_VERSION = "9844f5612881753b32cbeb3c440187d61989e59e"


def get_version(bld, dir):
    streamlink_path = dir.make_node("streamlink/__init__.py")
    with open(str(streamlink_path)) as fd:
        d = fd.read()
        m = re.search('__version__ = "(\d+\.\d+\.\d+)"', d)
        v = m and m.group(1) or "0.0.0"

    return "{0}.{1}".format(v, BUILD_NUMBER)


def configure(ctx):
    ctx.check_waf_version(mini='1.9.7')
    if not os.path.exists("streamlink-{0}".format(STREAMLINK_VERSION)):
        ctx.fatal("streamlink-{0} directory must exist, download and unzip streamlink-{0}.zip".format(STREAMLINK_VERSION))


def build(bld):
    streamlink_src = bld.path.make_node("streamlink-{0}/src".format(STREAMLINK_VERSION))
    bld(rule="patch -Nf ${SRC[0]} < ${SRC[1]} || true",
        source=[streamlink_src.make_node("streamlink/utils/__init__.py"), "utils.patch"],
        always=True)

    bld(rule='cp -r ${SRC} ${TGT}',
        source=streamlink_src.make_node("streamlink"),
        target=bld.path.get_bld().make_node("lib/streamlink"))

    bld(features="subst", source="addon.xml.in", target="addon.xml",
        APPNAME=APPNAME, VERSION=get_version(bld, streamlink_src))

    for f in ['LICENSE', 'changelog.txt', 'README.md', 'icon.png', 'resources',
              'addon.py', 'service.py', 'simpleplugin.py']:
        bld(rule='cp -r ${SRC} ${TGT}', source=bld.path.make_node(f), target=bld.path.get_bld().make_node(f))


def dist(ctx):
    ctx.algo = "zip"
    ctx.base_path = ctx.path.make_node(out)
    ctx.base_name = APPNAME  # set the base directory for the archive
    ctx.files = ctx.path.ant_glob(
        "build/**.xml build/**.md build/**.png build/LICENSE build/**.py build/lib/*.py build/lib/**/*.py "
        "build/resources/*.py  build/**/*.xml")
    ctx.arch_name = "{0}-{1}.{2}".format(APPNAME,
                                         get_version(ctx, ctx.path.make_node("build/lib")),
                                         ctx.ext_algo.get(ctx.algo, ctx.algo))

