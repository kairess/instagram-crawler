# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os, json
from io import open
from datetime import datetime
import urllib.request
from urllib.parse import urlparse
import pandas as pd

from inscrawler import InsCrawler
from inscrawler.settings import override_settings
from inscrawler.settings import prepare_override_settings

number = 200

usernames = pd.read_csv('usernames.txt', header=None, names=['name'])
print('[*] %d users' % (len(usernames)))

for i, username in usernames.iterrows():
  username = username['name']
  print(username)

  target_path = 'result_username'
  debug = True

  current_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

  target_img_path = os.path.join(target_path, '%s_%s' % (username, current_timestamp))
  output_filename = '%s_%s.csv' % (username, current_timestamp)
  output_path = os.path.join(target_path, output_filename)

  ins_crawler = InsCrawler(has_screen=debug)

  ins_crawler.login()
  results = ins_crawler.get_user_posts(username, number, detail=True)

  print('[*] %d results' % len(results))

  os.makedirs(target_path, exist_ok=True)
  os.makedirs(target_img_path, exist_ok=True)

  df = pd.DataFrame(columns=['key', 'caption', 'img_url', 'likes'])

  for result in results:
    # key, captions, img_urls, likes
    for img_url, caption in zip(result['img_urls'], result['captions']):
      if caption is not None and (('1 person' in caption and 'closeup' in caption) or ('사람 1명' in caption and '근접 촬영' in caption)):
        if img_url is None:
          continue

        parsed = urlparse(img_url)
        filename = parsed.path.split('/')[-1]
        result['filename'] = filename
        result['img_url'] = img_url
        result['caption'] = caption

        urllib.request.urlretrieve(img_url, os.path.join(target_img_path, filename))

        df_result = result.copy()
        del df_result['img_urls'], df_result['captions']

        df = df.append(df_result, ignore_index=True)

  df.to_csv(output_path, index=False)
