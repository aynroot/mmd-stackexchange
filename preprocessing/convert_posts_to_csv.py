""" 
Parses posts file (xml) and saves ids, titles and bodies of posts in csv format
"""

import csv
import os
import codecs
import io
import shutil
import argparse
import xmltodict

from os.path import join


def clean(x):
    # neo4j-import doesn't support: multiline (coming soon), quotes next to each other and escape quotes with '\""'
    return x.replace('\n', '').replace('\r', '').replace('\\', '').replace('"', '')


def open_csv(filename):
    return csv.writer(open(filename, 'w'), doublequote=False, escapechar='\\')


def replace_keys(row):
    new = {}
    for key, val in row.items():
        new[key.replace('@', '')] = val
    return new


def main(infile, outfile):
    posts = open_csv(outfile)
    posts.writerow(['id', 'title', 'body'])

    converted_cnt = 0
    for line in open(infile):
        line = line.strip()
        try:
            if line.startswith('<row'):
                el = xmltodict.parse(line)['row']
                el = replace_keys(el)                
                if el['PostTypeId'] == '1':                    
                    posts.writerow([
                        el['Id'],
                        clean(el.get('Title', '').encode("utf-8")),
                        clean(el.get('Body', '').encode("utf-8"))
                    ])
                converted_cnt += 1
        except Exception as e:
            print e        

    print converted_cnt, 'rows converted'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', help='input csv path', required=True)
    parser.add_argument('-o', '--out-file', help='output csv path', required=True)
    args = parser.parse_args()
    main(args.in_file, args.out_file)
