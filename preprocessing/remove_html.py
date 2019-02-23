"""
Removes html tags and preserves links from Posts.csv
"""

import re
import csv
import argparse
from bs4 import BeautifulSoup, NavigableString
from lxml.html.clean import Cleaner


def convert(html_body):        
    body_with_links = Cleaner(allow_tags=['a'], remove_unknown_tags=False, page_structure=False).clean_html(html_body)
    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body_with_links)    
    converted_body = Cleaner(remove_tags=['a'], remove_unknown_tags=False, page_structure=False).clean_html(body_with_links)
    return links, converted_body[len('<div>'):-len('</div>')]


def main(infile, outfile):
    posts = csv.reader(open(infile), doublequote=False, escapechar='\\')
    posts_converted = csv.writer(open(outfile, 'w'), doublequote=False, escapechar='\\')
    
    posts_converted.writerow(['id', 'title', 'body', 'links'])
    posts.next()
    
    i = 0
    for id, title, body in posts:       
        try: 
            links, body_converted = convert(body)        
        except Exception as e:
            print e
            continue
        posts_converted.writerow([id, title, body_converted, ' '.join(links)])
        if int(id) % 5000 == 0:
            print '.',
        i += 1

    print i, 'converted'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', required=True)
    parser.add_argument('-o', '--out-file', required=True)
    args = parser.parse_args()
    main(args.in_file, args.out_file)