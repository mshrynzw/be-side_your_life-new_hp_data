import json
import os
import shutil
from datetime import datetime


def set_common():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, 'conf', 'common.json'), 'r') as f:
        common_conf = json.load(f)
    
    # blogディレクトリのパスを絶対パスに変更
    common_conf['BLOG_DIR'] = os.path.join(base_dir, 'blog', '')
    return common_conf


def set_log():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, 'log')
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    with open(os.path.join(base_dir, 'conf', 'log.json'), 'r') as f:
        log_conf = json.load(f)
    log_conf["handlers"]["fileHandler"]["filename"] = os.path.join(log_dir, '{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M%S")))

    return log_conf
