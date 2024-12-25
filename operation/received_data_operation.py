import uuid
from datetime import datetime
from flask import request, json, g
from cfg import INCOME_DB, COLLECTION_NAME, UPLOAD_FOLDER
from utils import SaveFile, SaveDocument, GetDocument
import textwrap

class CreateData:
    def __init__(self):
        self.__data = json.loads(request.form.to_dict()['data'])
        self.__file_identifiers = {}
        self.__msg = ''

    def create(self):
        self.__gen_tracking_id()

        _attached = self.__data.pop("__attachments", [])
        f_name_list = [attachment['name'] for attachment in _attached if _attached]
        self.__save_files(f_name_list)

        self.__normalize_data(_attached)
        self.__save_data()

    def get_msg(self):
        return self.__msg

    def __gen_tracking_id(self):
        _st = str(uuid.uuid4()).replace("-", "")
        _st = _st[0:16]
        _st = textwrap.wrap(_st, 4)

        # _chunks, _chunk_size = len(_st), 4
        # _st = [_st[i:i + _chunk_size] for i in range(0, _chunks, _chunk_size)]
        self.__data['tracking_id'] = '-'.join(_st).upper()

    def __save_files(self, f_name_list):
        if f_name_list:
            try:
                _f = SaveFile(
                    root_dir=UPLOAD_FOLDER,
                    leaf_dir=self.__data["tracking_id"],
                    file_name_list=f_name_list
                )
                _f.save_form_data_files()
                self.__file_identifiers = _f.get_identifiers()
            except (Exception,) as e:
                g.error_handler.log_to_file(str(e))

                g.error_handler.handle_error("Something is wrong with files, request does not performed", 500)

    def __save_data(self):
        try:
            _save_doc = SaveDocument(
                db_name=INCOME_DB,
                collection_name=COLLECTION_NAME
            )
            _id = _save_doc.add_document(self.__data)
            g.success_handler.log_to_file(f"Success: created document from request. id: {_id}")
            self.__msg = f'Submission-Id: {_id}, {self.__data["tracking_id"]}'
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something is wrong with data, request does not performed", 500)

    def __normalize_data(self, _attached):
        if self.__file_identifiers and _attached:
            for i, _attachment in enumerate(_attached):
                _file_identifier = self.__file_identifiers[_attachment['name']]
                _attached[i] = _attached[i] | _file_identifier

        if _attached:
            self.__data['file_list'] = _attached

        self.__data['sent_status'] = 'No'
        self.__data['creation_date'] = str(datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        self.__data['sender_ip'] = request.environ['REMOTE_ADDR'] \
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None \
            else request.environ['HTTP_X_FORWARDED_FOR'] #behind a proxy
        #self.__data['source_url'] = request.base_url

class GetData:
    def __init__(self):
        self.__get_document_s = GetDocument(
            db_name=INCOME_DB,
            collection_name=COLLECTION_NAME
        )
    def get_file_data_by_unique_id(self, file_unique_id):
        self.__get_document_s.set_pipeline([
            {'$unwind': "$file_list"},
            {"$match": {'file_list.file_unique_id': file_unique_id}}
        ])
        try:
            _doc = self.__get_document_s.aggregate_collection()
            return _doc[0] if _doc is not None else None
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something went wrong, couldn't complete the operation. Please, try later", 500)

    def get_one(self, sent_status):
        self.__get_document_s.set_params({
            'sent_status': sent_status
        })
        try:
            _doc = self.__get_document_s.get_document()
            return _doc
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something went wrong, couldn't complete the operation. Please, try later", 500)

    def get_data_list(self, limit, sent_status=None, sort_sent_status=False):
        if isinstance(sent_status, list):
            self.__get_document_s.set_params({
                'sent_status': {'$in': sent_status}
            })
        else:
            self.__get_document_s.set_params({
                'sent_status': sent_status
            })
        if sort_sent_status:
            self.__get_document_s.set_sort_fields({
                'key': 'sent_status',
                'val': -1
            })

        try:
            _doc_list = self.__get_document_s.get_document_list(limit=limit)
            return _doc_list
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something went wrong, couldn't complete the operation. Please, try later", 500)

class UpdateData:
    def __init__(self):
        self.__save_document_s = SaveDocument(
            db_name=INCOME_DB,
            collection_name=COLLECTION_NAME
        )

    def change_document_status(self, doc_id, sent_status, notes):
        self.__save_document_s.set_params({
            'sent_status': sent_status,
            'notes': notes
        })
        try:
            self.__save_document_s.update_document_by_id(doc_id)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something went wrong, couldn't complete the operation. Please, try later", 500)