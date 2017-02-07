import sys
import os
import uuid
import xbmcgui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import streamlink
from streamlink.stream import HTTPStream, RTMPStream
from simpleplugin import Plugin

plugin = Plugin()


def first_or_none(x):
    if x and len(x) > 0:
        return x[0]


def store_stream_item(cid=None, **values):
    cache = plugin.get_storage()
    cid = cid or uuid.uuid4().hex
    try:
        data = cache[cid]
    except KeyError:
        data = {}
    data.update(values)
    cache[cid] = data

    return cid


def get_stream_item(cid):
    cache = plugin.get_storage()
    try:
        return cache[cid]
    except KeyError:
        return None



def generate_proxy_url(cache_id):
    http_port = plugin.get_setting('listen_port')
    return "http://localhost:{port}/proxy/{id}".format(port=http_port, id=cache_id)


@plugin.action()
def root(params):
    url = params.get("url")
    if not url:
        xbmcgui.Dialog().notification('Warning!', "No URL to stream provided")
        return []

    plugin.log_notice("Trying to find a stream to play on {0}".format(url))
    session = streamlink.Streamlink()

    streams = session.streams(url)

    qual = params.get('q', 'best')
    label = params.get('label', 'stream')
    stream = streams.get(qual)

    if stream is None:
        qlist = ','.join(streams.keys())
        plugin.log_error("Failed to find stream with the requested quality "
                         "({0}) with URL: {1} "
                         "(qualities available: {2})".format(qual, url, qlist or "N/A"))
        xbmcgui.Dialog().notification('Warning!', "No streams available for this URL, Geo-Locked?")
    else:
        if isinstance(stream, (HTTPStream,)):
            return Plugin.resolve_url(stream.url)
        elif isinstance(stream, (RTMPStream,)):
            rtmp = stream.params.pop('rtmp')
            args = ["{0}={1}".format(k, v) for k, v in stream.params.items()]
            return Plugin.resolve_url(play_item={
                'label': label,
                'path': '{0} {1}'.format(rtmp, " ".join(args))
            })
        else:
            cache_id = store_stream_item(url=url, quality=qual)

            return Plugin.resolve_url(generate_proxy_url(cache_id))


if __name__ == '__main__':
    plugin.run()
