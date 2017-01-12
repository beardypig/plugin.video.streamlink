import sys
import os

BUILD_NUMBER = os.environ.get("TRAVIS_BUILD_NUMBER", 0)
APPNAME = "plugin.video.streamlink"
STREAMLINK_ZIP = "https://github.com/streamlink/streamlink/archive/master.zip"
out = "build"


def get_version(bld):
    streamlink_path = bld.path.make_node("lib/streamlink")
    sys.path.insert(0, str(streamlink_path))
    import streamlink
    return "{0}.{1}".format(streamlink.__version__, BUILD_NUMBER)


def configure(ctx):
    ctx.check_waf_version(mini='1.9.7')


def build(bld):

    bld(rule='wget {zip} -O ${{TGT}}'.format(zip=STREAMLINK_ZIP), target="streamlink.zip")
    bld(rule='unzip -o ${SRC} ${TGT}/*', source='streamlink.zip', target=bld.path.get_bld().make_node('streamlink-master/src/streamlink'))
    bld(rule='cp -r ${SRC} ${TGT}', source=bld.path.get_bld().make_node("streamlink-master/src/streamlink"), target=bld.path.get_bld().make_node("lib"))

    bld(features="subst", source="addon.xml.in", target="addon.xml",
        APPNAME=APPNAME, VERSION=bld.env["VERSION"])

    for f in ['LICENSE', 'changelog.txt', 'README.md', 'icon.png', 'resources']:
        bld(rule='cp -r ${SRC} ${TGT}', source=bld.path.make_node(f), target=bld.path.get_bld().make_node(f))


def dist(ctx):
    ctx.algo = "zip"
    ctx.base_path = ctx.path.make_node(out)
    ctx.base_name = APPNAME  # set the base directory for the archive
    ctx.arch_name = "{0}-{1}.{2}".format(APPNAME, get_version(ctx), ctx.ext_algo.get(ctx.algo, ctx.algo))
    ctx.files = ctx.path.ant_glob(
        "build/**/*.xml build/*.md build/LICENSE build/**/*.xml build/lib/**")
