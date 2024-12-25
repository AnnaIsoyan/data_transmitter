# app
APP_HOST = '0.0.0.0'
APP_PORT = 5500
APP_PORT_DEBUG = 5501
DEBUG_MODE = True  # todo set to False in production

# external source and reciever configs
EXTERNAL_SOURCE_DATA_RECEIVER = ""
EXTERNAL_SOURCE_FILE_URL = ""
EXTERNAL_SOURCE_DATA_TOKEN = ''
EXTERNAL_SOURCE_DATA_STATUS_SENT = 'Yes'
EXTERNAL_SOURCE_DATA_STATUS_NOT_SENT = 'No'
EXTERNAL_SOURCE_DATA_STATUS_IN_PROCESS = 'In_process'
EXTERNAL_SOURCE_DATA_STATUS_ERROR = 'Error'
EXTERNAL_SOURCE_DATA_STATUS_TIMOUT = 'Timeout'

# to send back data
EXTERNAL_SOURCE_TRANSMITTER_ALLOWED_IP_LIST = []

# data structure example
INCOME_DATA_PARAM_LIST = {
    "param1": {  # req
        "type": 'list',
        "is_required": True
    },
    "param2": {  # req
        "type": 'dict',
        "is_required": True,
        "properties": {
            "param2_1": {
                "type": "str",
                "is_required": True
            },
            "param2_2": {
                "type": "str",
                "is_required": False
            },
            "param2_3": {
                "type": "str",
                "is_required": False
            },
        }
    },
    "param3": {  # req
        "type": 'dict',
        "is_required": True,
        "properties": {
            "param3_1": {
                "type": "datetime",
                "is_required": True
            },
            "param3_2": {
                "type": "datetime",
                "is_required": False
            },
            "param3_3": {
                "type": "datetime",
                "is_required": False
            },
        }
    },
    "param4": {
        "type": 'dict',
        "properties": {
            "param4_1": {
                "type": "datetime",
            }
        }
    },
    "__attachments": {
        "type": 'list',
        "properties": {
            "label": {
                "type": "str",
            },
            "name": {  # req
                "type": "str",
                "is_required": True,
            },
            "checksum": {
                "type": "str",
            },
        }
    },

}

# mongodb
#MONGODB_HOST = '127.0.0.1'
MONGODB_HOST = 'data_transmitter_mongo'
MONGODB_PORT = '27017'
MONGODB_USERNAME = 'my_superuser'
MONGODB_PASSWORD = 'qwerty'
MONGO_DBNAME_INCOME = 'income_data'
COLLECTION_NAME = 'data_tree'
DBNAME_MONITORING = 'monitoring'#todo perform
DATA_LIMIT = 20

#create indexes for incoming file search params
INDEX_PARAM_LIST = {
    MONGO_DBNAME_INCOME : {
        COLLECTION_NAME: {
            "file_list.file_unique_id" : 1,
            "sent_status": 1
        }
    }
}


# file expandable
NOT_ALLOWED_EXTENSIONS = [
    '.exe','.pif', '.application', '.gadget',
    '.msi', '.msp', '.com', '.scr', '.hta', '.cpl',
    '.msc', '.jar', '.bat', '.cmd', '.vb', '.vbs', '.js',
    '.jse', '.ws', '.wsf', '.wsc', '.wsh',
    '.ps1', 'ps1xml', '.ps2', '.ps2xml', '.psc1', '.psc2',
    '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml', '.msh2xml',
    '.scf', '.lnk', '.inf', '.reg', '.sh', '.py', '.ipynb', '.php'
    '.docm', '.dotm', '.xlsm', '.xlst', '.zsh', '.jsx'
    '.pptm', '.potm', '.ppam', '.ppsm', '.sldm', '.ppt', '.pptx'
]
ROOT_DIR = "/data"
UPLOAD_FOLDER = '/data/storages'
TOTAL_FILE_MAX_SIZE = 104857600  # bytes 100mb
SINGLE_FILE_MAX_SIZE = 52428800  # bytes 50mb

# log
RELATIVE_PATH = '/data/www/data_transmitter'
LOG_PATH = 'var/log'
ERROR_LOG_FILE_NAME = 'error'
SUCCESS_LOG_FILE_NAME = 'success'
API_INFO_LOG_DIR = 'api'
CRON_JOB_P_ID_FILE = 'cronjob'


def app_port():
    return APP_PORT_DEBUG if DEBUG_MODE else APP_PORT


def get_collection_index_param_list(db_name, collection_name):
    if not db_name in INDEX_PARAM_LIST.keys():
        return {}
    if not collection_name in INDEX_PARAM_LIST[db_name].keys():
        return {}
    return INDEX_PARAM_LIST[db_name][collection_name]

def is_allowed_ip(_ip):
    _f_path = RELATIVE_PATH+"/cfg/allowed_ip_list"
    with open(_f_path, 'r') as f:
        _ip_list = [l.rstrip() for l in f]

    return True if _ip in _ip_list else False

