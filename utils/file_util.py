import os
from datetime import date
from flask import request, g


def gen_file_path(_date, _root_dir, _leaf_dir):
    _date = _date.split('.')
    _d, _m, _y = [str(int(_p)) for _p in _date]

    return "/".join([_root_dir, _y, _m, _d, _leaf_dir])

class FileUtil:
    def __init__(self, file_name_list):
        self._file_name_list = file_name_list


class SaveFile(FileUtil):
    def __init__(self,
                 root_dir,
                 file_name_list,
                 leaf_dir=''):
        super().__init__(file_name_list)
        self.__root_dir = root_dir
        self.__leaf_dir = leaf_dir
        self.__identifiers = {}

    def get_identifiers(self):
        return self.__identifiers

    def save_form_data_files(self):
        _file_path, _date = self.__gen_unique_path()

        for f_name in self._file_name_list:
            _file = g.pop(f_name)

            f = request.files.getlist(f_name)[0]
            f.save(os.path.join(_file_path, _file["_file_name"]))
            f.close()

            self.__identifiers[f_name] = {
                'file_unique_id': _file["_uuid"],
                'file_date': _date,
                'file_ext': _file["_ext"],
                'file_content_type': _file["_mimetype"],
                'file_content_length': _file["_content_length"],
                'file_name': _file["_file_original_name"],
                #'file_checksum': _checksum
            }

    # todo provide
    def save_single_file(self):
        pass

    def __gen_unique_path(self):
        _date = date.today()
        year, month, day = _date.year, _date.month, _date.day

        _p = "/".join([self.__root_dir, str(year), str(month), str(day)])

        if self.__leaf_dir:
            _p += "/" + self.__leaf_dir

        os.makedirs(_p, exist_ok=True)
        return _p, str(_date.strftime('%d.%m.%Y'))