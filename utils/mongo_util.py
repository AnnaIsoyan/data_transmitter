from pymongo import MongoClient
import urllib.parse as parse
from cfg import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD, index_params
from flask import g
from pymongo.errors import PyMongoError

class Connection:
    def __init__(self):
        try:
            self._client = MongoClient(self.__uri())
        except PyMongoError as e:
            g.error_handler.log_to_file(str(e))
            raise ConnectionError(str(e))

    def __del__(self):
        self._client.close()
        self.__client = None

    @staticmethod
    def __uri():
        return f"mongodb://{MONGODB_USERNAME}:{parse.quote_plus(MONGODB_PASSWORD)}@{MONGODB_HOST}:{MONGODB_PORT}"


class MongoUtil(Connection):
    def __init__(self):
        super().__init__()
        self._database = None
        self._collection = None

    def is_exist(self, key, value):
        return True if self._collection.count_documents({key: value}, limit=1) != 0 else False

    def _add_database(self, db_name):
       self._database = self._client[db_name]

    def _add_collection(self, coll):
        _is_exist = False
        self._collection = self._database.get_collection(coll)
        if self._collection is not None:
            _is_exist = True
        if not _is_exist:
            self._collection = self._database.create_collection(coll)
            _ind_dict = index_params(db_name=self._database.name, collection_name=coll)
            if _ind_dict:
                self._collection.create_index(_ind_dict)

    def _count_documents(self):
        return self._collection.estimated_document_count()


class DocumentUtil(MongoUtil):
    def __init__(self, db_name, collection_name):
        super().__init__()
        self._add_database(db_name)
        #self._collection_name = collection_name
        self._add_collection(collection_name)
        self._params = {}
        self._fields = {}

    def set_params(self, params_dic):
        self._params = params_dic

    def set_fields(self, fields_dic):
        self._fields = fields_dic


class SaveDocument(DocumentUtil):

    def add_document(self, document):
        document['_id'] = self.__next_id()
        try:
            _last_inserted_id = self._collection.insert_one(document, 1).inserted_id
        except PyMongoError as e:
            g.error_handler.log_to_file(str(e))
            raise ConnectionError(str(e))

        return _last_inserted_id

    def update_document_by_id(self, doc_id):
        self._collection.update_one(
            { '_id': doc_id},
            {"$set": self._params}
        )

    def __next_id(self):
        return self._count_documents() + 1


class GetDocument(DocumentUtil):
    def __init__(self, db_name, collection_name):
        super().__init__(db_name, collection_name)
        #todo must provide mongo query builder
        self.__pipeline = None
        self.__sort_fields = {}

    def set_pipeline(self, new_pipeline):
        self.__pipeline = new_pipeline

    def set_sort_fields(self, sort_dic):
        self.__sort_fields = sort_dic

    def get_document_by_id(self, doc_id):
        _doc = self._collection.find_one({'_id': doc_id}, self._fields)
        return _doc

    def get_document(self, doc_id=None):
        if doc_id:
            self._params = self._params | {'_id': doc_id}
        _doc = self._collection.find_one(self._params, self._fields)
        return _doc

    def aggregate_collection(self):
        if not self.__pipeline:
            return None
        _found_list = self._collection.aggregate(
            pipeline=self.__pipeline
        )
        if _found_list is None:
            return None
        doc_list = []
        for _doc in _found_list:
            doc_list.append(_doc)

        return doc_list


    def get_document_list(self, limit=0):
        if not self.__sort_fields:
            _doc_list = [_doc for _doc in self._collection.find(self._params, self._fields, limit=limit)]
        else:
            #works only with one field sorting. No time, must provide mongo query builder
            sort_key = self.__sort_fields['key']
            sort_val = self.__sort_fields['val']
            _doc_list = [_doc for _doc in self._collection.find(self._params, self._fields, limit=limit).sort(sort_key, sort_val)]
        return _doc_list

