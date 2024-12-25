import requests
from operation import GetData, UpdateData
from cfg import EXTERNAL_SOURCE_DATA_STATUS_NOT_SENT, EXTERNAL_SOURCE_DATA_STATUS_SENT, \
    EXTERNAL_SOURCE_DATA_STATUS_ERROR, EXTERNAL_SOURCE_DATA_STATUS_IN_PROCESS, UPLOAD_FOLDER, EXTERNAL_SOURCE_DATA_STATUS_TIMOUT
from cfg import RECEIVER_HOST, DATA_TOKEN
from cfg import FILE_URL, ROOT_DIR, CRON_JOB_P_ID_FILE, DATA_LIMIT
from datetime import datetime, timedelta
import json
import os
from utils import gen_file_path
import hashlib
from flask import g


class SchedulerWorker:
    def __init__(self):
        self.__get_data_s = GetData()
        self.__update_data_s = UpdateData()
        self.__send_data = {}

    def do_work(self):
        _data_list = self.__get_data_list()
        if not _data_list:
            return

        pid = os.getpid()
        _path = ROOT_DIR+"/"+CRON_JOB_P_ID_FILE
        f = open(_path, 'w')
        f.write(f"pid: {pid}")
        f.close()

        self.__change_data_status(_data_list, EXTERNAL_SOURCE_DATA_STATUS_NOT_SENT)
        for _data in _data_list:
            _id = _data['_id']
            self.__prepare_send_data(_data)

            try:
                response = requests.post(RECEIVER_HOST, json=self.__send_data, timeout=10)

                if response.status_code != requests.codes.ok:
                    self.__change_data_status([_data], EXTERNAL_SOURCE_DATA_STATUS_ERROR, response.text)
                    return

                is_error = False
                msg = ''
                sent_status = EXTERNAL_SOURCE_DATA_STATUS_SENT
                if not response.text:
                    msg = 'text field is empty in response'
                    g.error_handler.log_to_file(msg)
                    is_error = True
                    sent_status = EXTERNAL_SOURCE_DATA_STATUS_ERROR

                if not is_error:
                    msg, txt_code = self.__validate_response_text(response)

                    if txt_code != requests.codes.ok:
                        sent_status = EXTERNAL_SOURCE_DATA_STATUS_ERROR

                self.__change_data_status([{'_id': _id}], sent_status, msg)
            except requests.exceptions.Timeout as e:
                g.error_handler.log_to_file(f"Crone: _id:{_id} Timeout Error - {str(e)}")
                self.__change_data_status(
                    [{'_id': _id}],
                    EXTERNAL_SOURCE_DATA_STATUS_TIMOUT,
                    f"remote server did not answer. error_msg: {str(e)}")
                pass
            except requests.RequestException as e:
                g.error_handler.log_to_file(f"Crone: _id:{_id} RequestException - {str(e)}")
                self.__change_data_status(
                    [{'_id': _id}],
                    EXTERNAL_SOURCE_DATA_STATUS_ERROR,
                    f"other request exception. error_msg: {str(e)}")
                pass
            except KeyboardInterrupt:
                g.error_handler.log_to_file(f"Crone: _id:{_id} KeyboardInterrupt")
                self.__change_data_status(
                    [{'_id': _id}],
                    EXTERNAL_SOURCE_DATA_STATUS_ERROR,
                    "someone closed the program")
                pass
            except (Exception,) as e:
                g.error_handler.log_to_file(f"Crone: _id:{_id} Exception - {str(e)}")
                self.__change_data_status(
                    [{'_id': _id}],
                    EXTERNAL_SOURCE_DATA_STATUS_ERROR,
                    f"unknown exception: {str(e)}")
                pass
        os.remove(_path)
        del g.success_handler
        del g.error_handler
    def __get_data_list(self):
        #self.__change_data_status([{'_id': 10}], status=MULBERRY_DATA_STATUS_NOT_SENT)
        if self.__get_data_s.get_one(EXTERNAL_SOURCE_DATA_STATUS_IN_PROCESS) is not None:
            return []
        return self.__get_data_s.get_data_list(
            limit=DATA_LIMIT,
            sent_status=[EXTERNAL_SOURCE_DATA_STATUS_ERROR, EXTERNAL_SOURCE_DATA_STATUS_TIMOUT, EXTERNAL_SOURCE_DATA_STATUS_SENT],
            sort_sent_status=True
        )

    def __change_data_status(self, data_list, status, notes=''):
        for _data in data_list:
            self.__update_data_s.change_document_status(_data["_id"], status, notes)

    def __prepare_send_data(self, _data):
        if 'file_list' in _data:
            for i, file_data in enumerate(_data['file_list']):

                _path = gen_file_path(file_data['file_date'], UPLOAD_FOLDER, _data["tracking_id"])

                f = open(_path+"/"+file_data['file_unique_id']+file_data['file_ext'], 'rb')
                _content = f.read()
                _checksum = hashlib.sha256(_content).hexdigest()
                f.close()

                file_data = {
                    "name": file_data['file_name'],
                    "label": file_data['label'],
                    "file_url": FILE_URL + "/download/" + file_data['file_unique_id'],
                    'file_content_type': file_data['file_content_type'],
                    "checksum": _checksum
                }
                _data['file_list'][i] = file_data

            '''_data = {
                "submission_id": _data["_id"],
                "tracking_id": _data["tracking_id"],
                "sender_ip": _data["sender_ip"],
                'uuid': _data["uuid"],
                'sys_title': _data["sys_title"],
                'sys_reg_num': _data["sys_reg_num"],
                'ext_deadline': _data["ext_deadline"] if "ext_deadline" in _data else {},
                'sys_deadline_notes': _data["sys_deadline_notes"] if "sys_deadline_notes" in _data else [],
                "file_list": _data["file_list"] if 'file_list' in _data else []
            }'''
            '''if "first" in _data["ext_deadline"].keys() and _data["ext_deadline"]['first']:
                _data["ext_deadline"]["first"] = self.append_time(_data["ext_deadline"]["first"])

            if "second" in _data["ext_deadline"].keys() and _data["ext_deadline"]['second']:
                _data["ext_deadline"]["second"] = self.append_time(_data["ext_deadline"]["second"])

            if "third" in _data["ext_deadline"].keys() and _data["ext_deadline"]['third']:
                _data["ext_deadline"]["third"] = self.append_time(_data["ext_deadline"]["third"])'''

        _data.pop('sent_status')
        _data['submission_id'] = _data["_id"]
        _data.pop('_id')
        _data.pop('notes') if 'notes' in _data else None

        self.__send_data = {
            "token": DATA_TOKEN,
            "data": _data
        }
        #self.__send_data = json.dumps(self.__send_data, ensure_ascii=False).encode('utf8')

    @staticmethod
    def append_time(_date):
        _d = datetime.strptime(_date, '%Y-%m-%d')
        _t = timedelta(minutes=0)
        _d = _d + _t
        _d = _d.strftime('%Y-%m-%d %H:%M')
        return str(_d)

    def __validate_response_text(self, response):
        _txt_parsed = json.loads(response.text)
        _status_data = ''
        _code_data = ''
        _msg_data = ''

        _status = _txt_parsed['status']
        if not _status:
            msg = 'status field is empty in text'
            g.error_handler.log_to_file(msg)

        if _txt_parsed['data'] and isinstance(_txt_parsed['data'], dict):
            _status_data = _txt_parsed['data']['status']
            _code_data = _txt_parsed['data']['code']
            _msg_data = _txt_parsed['data']['message']
            if not _status_data:
                msg = '_status_data field is empty in text'
                g.error_handler.log_to_file(msg)
            if not _code_data:
                msg = '_code_data field is empty in text'
                g.error_handler.log_to_file(msg)

        msg = f"status: {_status}, data.status: {_status_data}, data.code: {_code_data}, data.message: {_msg_data}"

        return msg, _code_data


