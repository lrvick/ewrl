import urllib
import urlparse
import re
import json
import lxml.html
try:
    import eventlet
    from eventlet.green import urllib2
except ImportError:
    import urllib2

def batch_url_expand(url_list):
    def batch_expand(url):
        return url_expand(url,True)
    completed_urls={}
    pool = eventlet.GreenPool()
    for expanded_url in pool.imap(batch_expand, url_list):
        yield expanded_url

def url_clean(url):
    domain, query = urllib.splitquery(url)
    new_url = None
    if query:
        query = re.sub('utm_(source|medium|campaign)\=([^&]+)&?', '', query)
        new_url = urlparse.urljoin(domain, "?"+query)
    else:
        new_url = domain
    return new_url

def url_expand(url,return_orig=False):
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    url = url_clean(url)
    orig_url = url
    last_url = None
    n = 0
    while unicode(last_url) != unicode(url):
        n += 1
        if n > 2:
            url = last_url
        else:
            try:
                request = urllib2.Request(url,None,headers)
                response = urllib2.urlopen(request,None,1)
                last_url = url
                url = url_clean(response.url)
            except Exception,e:
                if last_url is not None:
                    url = last_url
                break
    url=unicode(url)
    if return_orig:
        return orig_url,url
    else:
        return url

def url_data(url):
    feed = None
    title = None
    data = None
    try:
        data = urllib2.urlopen(url, None, 2).read(6000)
        data = re.sub('\n|\r','',data)
    except:
        pass
    if data:
        html = lxml.html.fromstring(data)
        try:
            feed = html.xpath('//link[@type="application/rss+xml"]/@href')[0]
            if not 'http' in feed:
                feed = "%s%s" % (url,feed)
        except:
            pass
        try:
            title = html.find('.//title').text
        except:
            pass
    return [title, feed]

def base58(n):
    alphabet='123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    result = ''
    while n >= 58:
        div,mod = divmod(int(n),58)
        result = alphabet[mod] + result
        n = div
    result = alphabet[n] + result
    base_count=len(alphabet)
    return result

def url_shorten(url,service='goo.gl'):
    short_url = None
    if not re.match('https?://',url):
        raise Exception('URL must start with "http://"')
    if 'youtube' in url:
        parsed_url = urlparse.urlsplit(url)
        video_id = urlparse.parse_qs(parsed_url.query)['v'][0]
        short_url = 'http://youtu.be/%s' % video_id
    elif 'flickr' in url:
        parsed_url = urlparse.urlsplit(url)
        photo_id = parsed_url.path.split('/')[3]
        base58_photo_id = base58(photo_id)
        short_url = 'http://flic.kr/p/%s' % base58_photo_id
    elif 'wordpress' in url:
        html = lxml.html.parse(url)
        short_url = html.xpath('//link[@rel="shortlink"]/@href')[0]
    else:
        if service == 'goo.gl':
            try:
                request = urllib2.Request('http://goo.gl/api/url','url=%s'%urllib.quote(url),{'User-Agent':'toolbar'})
                result = urllib2.urlopen(request).read()
                dict_result = json.loads(result)
                short_url = dict_result['short_url']
            except urllib2.HTTPError, e:
                print e
        else:
            if service == 'tinyurl':
                request_url='http://tinyurl.com/api-create.php?url='+url
            elif service == 'is.gd':
                request_url='http://is.gd/api.php?longurl='+url
            short_url = urllib2.urlopen(request_url).read()
    return short_url

if __name__=="__main__":
    print "\n-- Testing ewrl --"
    print "\nFetching Title and RSS feed of 'http://theoatmeal.com/'"
    print url_data('http://theoatmeal.com/')
    print "\nExpanding 'http://bit.ly/fwGp4w':"
    print url_expand('http://bit.ly/fwGp4w')
    print "\nShortening 'http://www.youtube.com/watch?v=dQw4w9WgXcQ':"
    print url_shorten('http://www.youtube.com/watch?v=dQw4w9WgXcQ')
    print "\nShortening 'http://en.blog.wordpress.com/2009/08/14/shorten/':"
    print url_shorten('http://en.blog.wordpress.com/2009/08/14/shorten/')
    print "\nShortening 'http://www.flickr.com/photos/lrvick/5684925240/':"
    print url_shorten('http://www.flickr.com/photos/lrvick/5684925240/')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with goo.gl:"
    print url_shorten('https://github.com/lrvick/ewrl/')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with is.gd:"
    print url_shorten('https://github.com/lrvick/ewrl/','is.gd')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with tinyurl:"
    print url_shorten('https://github.com/lrvick/ewrl/','tinyurl')
