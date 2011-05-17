import httplib
import urlparse
import urllib
import re
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

def url_data(url,**kwargs):
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

if __name__=="__main__":
    print "-- Testing ewrl --\n\n"
    print url_expand('http://bit.ly/fwGp4w')
    print "https://github.com/lrvick/ewrl/blob/master/ewrl.py"
    print url_data
