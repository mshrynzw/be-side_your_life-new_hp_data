import json
import os
import shutil
from datetime import datetime


def set_common():
    with open('./conf/common.json', 'r') as f:
        common_conf = json.load(f)

    return common_conf


def set_log():
    with open('./conf/log.json', 'r') as f:
        try:
            shutil.rmtree('./log/')
        except FileNotFoundError:
            os.mkdir('./log/')
        log_conf = json.load(f)
    log_conf["handlers"]["fileHandler"]["filename"] = './log/{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

    return log_conf
