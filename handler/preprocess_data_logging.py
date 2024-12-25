import os
from cfg.config import LOG_PATH, RELATIVE_PATH, API_INFO_LOG_DIR
from datetime import date
import json

def save_mulberry_api_log(data):
    _date = str(date.today())
    _file_path = RELATIVE_PATH+"/"+LOG_PATH+"/"+API_INFO_LOG_DIR+"/"+_date

    os.makedirs(_file_path, exist_ok=True)
    _file_path += "/"+_date+".log"

    _obj =  json.dumps(data, ensure_ascii=False)

    f = open(_file_path, 'a', encoding='utf-8')
    f.write(f"{_obj}\n")
    f.close()



