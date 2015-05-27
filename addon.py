#!/usr/bin/env python2
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages',
                                'livestreamer', 'src'))
import livestreamer
import uuid
from xbmcswift2 import Plugin
from livestreamer.stream import HTTPStream, RTMPStream

plugin = Plugin()

def get_proxy_cache(cid=None, region='proxy-cache', ttl=5, **values):
    # cache the info for a short period of time
    # the cache will be refreshed by the proxy daemon to keep the base urls up-to-date.
    cache = plugin.get_storage(region, TTL=ttl)
    cache.update(**values)

    return cid or uuid.uuid4().hex, cache

def generate_proxy_url(cache_id):
    http_port = plugin.get_setting('listen_port', int)
    return "http://localhost:{port}/proxy/{id}".format(port=http_port, id=cache_id)

@plugin.route('/play')
def play_stream():

    url = plugin.request.args.get('url')
    if not url:
        plugin.notify("No URL to stream provided")
        return
    session = livestreamer.Livestreamer()

    streams = session.streams(url)

    qual = plugin.request.args.get('q', 'best')
    stream = streams.get(qual)

    if stream is None:
        qlist = ','.join(streams.keys())
        plugin.log.error("Failed to find stream with the requested quality "
                         "({0}) with URL: {1} "
                         "(qualities available: {2})".format(qual, url, qlist or "N/A"))
        plugin.notify("No streams available for this URL")
    else:
        if isinstance(stream, (HTTPStream, )):
            plugin.set_resolved_url(stream.url)
        elif isinstance(stream, (RTMPStream,)):
            plugin.play_video(stream.params)
        else:
            cache_id, cache = get_proxy_cache(stream=stream)

            plugin.set_resolved_url(generate_proxy_url(cache_id))

if __name__ == '__main__':
    plugin.run()
