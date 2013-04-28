#!/usr/bin/env python3


import argparse
from collections import namedtuple, OrderedDict
from html.parser import HTMLParser
import io
import logging
import os
import re
import sys
import urllib.request as request
from urllib.error import URLError


DEFAULT = 'videourl'
H264 = 'videourl_h264'
MP4 = 'videourl_mp4'
#M3U = 'videourl_m3u8'
MEDIA_TYPES = {'DEFAULT':DEFAULT, 'H264':H264, 'MP4':MP4} #, 'M3U':M3U}

CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE
#EXCEPTIONS = (Exception, BaseException, BufferError)


def set_log_levels():
    logging.addLevelName(logging.DEBUG-1, 'NOLOG')
    levels = OrderedDict({'NOLOG':logging.DEBUG-1})
    for level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        levels[level] = getattr(logging, level)
    return levels

LOGNAME = os.path.basename(__file__)
LOGLEVELS = set_log_levels()


class MediaTypeError(Exception):
    pass

class VideoParser(HTMLParser):
    def __init__(self, *a, **k):
        super().__init__(*a,**k)
        self._video_links = []
    @property
    def video_links(self):
        return tuple(self._video_links)
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs = dict(attrs)
            name = attrs.get('name', '')
            if name.startswith('videourl'):
                maybe_url = attrs.get('content')
                if maybe_url:
                    self._video_links.append((name, maybe_url))

def get_args (args=None):
    epilog = """---
Run tests with:
% {python} -m unittest -v {prog}
---""".format(prog=sys.argv[0], python=sys.executable)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument('url', help='url')
    parser.add_argument('-c', '--continue',
                        dest='continue_', action='store_true',
                        help='when file, try to resume download.')
    parser.add_argument('-l', '--log-level',
                        dest='loglevel', choices=tuple(LOGLEVELS.keys()),
                        default='INFO', metavar='LEVEL',
                        help='set log level: %(choices)s. Default %(default)s')
    parser.add_argument('-s', '--chunk-size',
                        dest='chunk_size', default=CHUNK_SIZE,
                        metavar='BYTES', help='default: %(default)s')
    parser.add_argument('-S', '--show-media-type',
                        dest='only_show', action='store_true',
                        help='''show the available media types
                        for the given url and exit''')
    parser.add_argument('-t', '--media-type',
                        dest='mtype', default='DEFAULT',
                        choices=MEDIA_TYPES.keys(),
                        help='''choose the media type to donwload
                        Choices: %(choices)s, default to %(default)s''')
    parser.add_argument('-o', '--output',
                        dest='out', default=None, metavar='PATH',
                        help='''output name. If not provided, use
                        the file basename and save it in the current dir.
                        If %(metavar)s is a directory, save in it using
                        the downloading file basename''')
    parser.add_argument('-O', '--overwrite',
                        dest='overwrite', action='store_true',
                        help='overwrite an already existent output file')
    parser.add_argument('-u', '--user-agent',
                        dest='ua', help='set user agent')
    return parser.parse_args(args)

def get_available_types(video_info):
    """video_info => an iterable like ones returned by video_links"""
    avail = []
    for vinfo in video_info:
        for type_name, type_value in MEDIA_TYPES.items():
            if vinfo.type == type_value:
                avail.append(type_name)
    return avail

def get_request (url):
    try:
        req = request.urlopen(url)
        if req is None:
            raise URLError("ERROR: no handler can handles the request")
    except URLError as err:
        logging.getLogger(LOGNAME).error(err)
        raise
    return req

def video_links (url):
    """Param:
    url => where to search for video links

    Yields namedtuple for available videos found in url.
    Those namedtuples has two fields, 'type' which store
    the type of this media, and 'url'.

    Returns: a generator of the above-mentioned namedtuples
    """
    get_request()
    parser = VideoParser(strict=False)
    parser.feed(req.read().decode('utf-8'))
    for vtype, link in parser.video_links:
        yield namedtuple('VideoInfo', 'type, url')(vtype, link)


def set_user_agent (user_agent):
    opener = request.build_opener()
    headers = dict(opener.addheaders)
    headers['User-agent'] = user_agent
    opener.addheaders = list(headers.items())
    request.install_opener(opener)

def seek_request (req, size, whence=os.SEEK_SET):
    logger = logging.getLogger(LOGNAME)
    logger.info('seek_request START')
    if req.seekable():
        req.seek(size, whence)
    else:
        req.read(size) #XXX+TODO: read chunks instead
    logger.info('seek_request END')

def save_stream (stream_in, stream_out, chunk_size):
    read = 0
    while True:
        buff = stream_in.read(chunk_size)
        read += len(buff)
        if not buff:
            break
        stream_out.write(buff)
    return read

def save_video(url, dest=None, chunk_size=CHUNK_SIZE,
               continue_=True, overwrite=False):
    logger = logging.getLogger(LOGNAME)
    req = get_request(url)
    content_type = req.getheader('Content-Type', 'UNKNOWN')
    if not re.match('^video/.*', content_type):
        logger.warning("{} seems not a video file [content-type: {}]".format(
                req.url, content_type))
    if dest:
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(req.url))
    else:
        dest = os.path.basename(req.url)
    length = req.length
    try:
        with open(dest, 'r+b') as out:
            read = out.seek(0, os.SEEK_END)
    except IOError:
        read = 0
    if read > 0:
        if not overwrite:            
            seek_request(req, read)
        else:
            read = 0
    while True:
        with open(dest, 'a+b') as out:
            read += save_stream(req, out, chunk_size)
            if read != length:
                if continue_:
                    out.seek(read, os.SEEK_SET)
                    req = get_request(url)
                    seek_request(req, read)
                    logger.info("download interrupted ({}/{} bytes), "
                                "resuming...".format(read, length))
                else:
                    logger.warning(
                        "total size mismatch {} != {}".format(read, length))
                    break
            else:
                break


def main():
    args = get_args()
    logging.basicConfig(format='%(name)s [%(levelname)s] %(message)s',
                        level=LOGLEVELS[args.loglevel])
    if args.ua:
        set_user_agent(args.ua)
    video_info = tuple(video_links(args.url))
    available_types = get_available_types(video_info)
    if args.only_show:
        print('available media types:', ','.join(available_types))
        return
    for vinfo in video_info:
        if vinfo.type == MEDIA_TYPES[args.mtype]:
            save_video(vinfo.url, args.out,
                       args.chunk_size, args.continue_, args.overwrite)
            break
    else:
        msg = "{} not available. Known types: {}"
        raise MediaTypeError(msg.format(args.mtype, available_types))


if __name__ == '__main__':
    main()
    sys.exit(0)


import random
import string
import unittest

def random_string(n):
    return ''.join(random.choice(string.ascii_letters)
                   for _ in range(n))

class TestMisc(unittest.TestCase):

    def testLogLevels(self):
        ld = set_log_levels()
        for k,v in ld.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, int)
            if k != 'NOLOG': # custom add, skip
                self.assertTrue(hasattr(logging, k))
                self.assertEqual(getattr(logging, k), v)
        self.assertEqual(list(ld.values()),
                         list(sorted(ld.values())))

    def testUserAgent(self):
        for _ in range(50):
            ua = random_string(random.randint(1,100))
            set_user_agent(ua)
            self.assertEqual(
                ua,
            dict(request._opener.addheaders)['User-agent'])


class TestStreams(unittest.TestCase):

    def testSeekRequest(self):
        for i in range(50):
            data = bytes(random_string(random.randint(5, 200)), 'utf-8')
            length = len(data)
            size = random.randrange(length)
            fake_req = io.BytesIO(data)
            if i%2:
                fake_req.seekable = lambda *a:False
            seek_request(fake_req, size, 0)
            self.assertEqual(len(fake_req.read()), length-size)

    def testSaveStream(self):
        for i in range(50):
            data = bytes(random_string(random.randint(200, 1200)), 'utf-8')
            instream = io.BytesIO(data)
            outstream = io.BytesIO()
            if i%2:
                chunk_size = int(20*len(data)/100) 
            else:
                chunk_size = CHUNK_SIZE
            save_stream(instream, outstream, chunk_size)
            instream.seek(0,0)
            outstream.seek(0,0)
            self.assertEqual(instream.read(), outstream.read())


class TestVideoParser(unittest.TestCase):
    HTML_DATA_TEST = (
        ('''<html><body>
<meta name="x:description" content="xxxxa."/>
<meta content="article" property="type"/>
<meta name="TV" content="2013"/>
<meta name="keywords" content="spam spam spam"/>
<meta name="tipo" content="Video"/>
<meta name="videourl" content="videourl"/>
<meta name="videourl_h264" content="videourl_h264"/>
<meta name="videourl_m3u8" content="videourl_m3u8"/>
<meta property="title" content="foo bar baz"/>
<meta name="subtitle" content=""/>
<meta property="odescription" content="xxx"/>
</body></html>''', ('videourl', 'videourl_h264', 'videourl_m3u8')),
        ('''<meta name="TV" content="2013"/>
<meta name="keywords" content="spam spam spam"/>
<meta name="tipo" content="Video"/>
<meta name="videourl" content="videourl"/>''', ('videourl',)),
        ('''<meta content="article" property="type"/>
<meta name="TV" content="2013"/>
''', ()),
        ('<html><body></body></html>', ()))

    def testVideoParser(self):
        for data, results in self.HTML_DATA_TEST:
            parser = VideoParser(strict=False)
            parser.feed(data)
            links = parser.video_links
            self.assertEqual(len(links), len(results))
            for vtype, link in links:
                self.assertEqual(vtype, link)
