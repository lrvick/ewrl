import httplib
import urlparse
import urllib
import urllib2
import re

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
        url_expand(current_url,n,original_url)

def url_title(url,**kwargs):
    request = urllib2.Request(url)
    data = None
    try:
        response = urllib2.urlopen(request)
        data = response.read()
    except urllib2.HTTPError:
        pass
    except urllib2.URLError:
        pass
    except httplib.BadStatusLine:
        pass
    except httplib.InvalidURL:
        pass
    except httplib.IncompleteRead:
        data = None
    except ValueError:
        data = None
    if data:
        if '<title>' in data:
            headers = response.info()
            content_type = headers.get('content-type',None)
            if content_type:
                raw_encoding = content_type.split('charset=')[-1]
                if 'text/html' in raw_encoding:
                    encoding = 'unicode-escape'
                else:
                    encoding = raw_encoding
                title_search = re.search('(?<=<title>).*(?=<\/title>)',data)
                if title_search:
                    try:
                        title = unicode(title_search.group(0),encoding)
                        return title
                    except Exception, e:
                        return False
            else:
                return False
