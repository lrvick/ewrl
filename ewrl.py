import httplib
import urlparse
import urllib
import urllib2
import re
import json
import lxml.html

def url_clean(url):
    domain, query = urllib.splitquery(url)
    new_url = None
    if query:
        query = re.sub('utm_(source|medium|campaign)\=([^&]+)&?', '', query)
        new_url = urlparse.urljoin(domain, "?"+query)
    else:
        new_url = domain
    return new_url

def url_expand(url,n=1,original_url=None,**kwargs):
    if n == 1:
        original_url = url
    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
    parsed_url = urlparse.urlsplit(url)
    request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
    response = None
    current_url = None
    try:
        connection = httplib.HTTPConnection(parsed_url.netloc)
    except httplib.InvalidURL:
        return False
    try: 
        connection.request('HEAD', request, "", headers)
        response = connection.getresponse()
    except Exception, e:
        return False
    if response:
        location = response.getheader('Location')
        if location:
            content_header = response.getheader('Content-Type');
            if content_header:
                encoding = content_header.split('charset=')[-1]
                try:
                    current_url = unicode(location, encoding)
                except LookupError:
                    pass
    n += 1
    if n > 3 or current_url == None:
        url = url_clean(url)
        return url
    else:
        return url_expand(current_url,n,original_url)

def url_data(url):
    feed = None
    title = None
    html = lxml.html.parse(url)
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
    print "\nShortening 'http://www.flickr.com/photos/lrvick/5684925240/':"
    print url_shorten('http://www.flickr.com/photos/lrvick/5684925240/')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with goo.gl:"
    print url_shorten('https://github.com/lrvick/ewrl/')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with is.gd:"
    print url_shorten('https://github.com/lrvick/ewrl/','is.gd')
    print "\nShortening 'https://github.com/lrvick/ewrl/' with tinyurl:"
    print url_shorten('https://github.com/lrvick/ewrl/','tinyurl')
    
