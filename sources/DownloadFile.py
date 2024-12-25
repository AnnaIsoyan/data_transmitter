from flask_restful import Resource
from flask import send_from_directory, g
from decorator import monitor_ip
from operation import GetData
from cfg import UPLOAD_FOLDER
from utils import gen_file_path

class DownloadFile(Resource):
    @monitor_ip
    def get(self, unique_id):
        if not unique_id:
            msg = 'Bad request. Unique_number is missing'
            g.error_handler.log_to_file(msg)
            g.error_handler.handle_error(msg, 400)
        try:
            _get_data_s = GetData()
            _file_data = _get_data_s.get_file_data_by_unique_id(unique_id)
            if _file_data is None:
                msg = 'Bad request. Unique_number is incorrect'
                g.error_handler.log_to_file(msg)
                g.error_handler.handle_error(msg, 400)

            _date = _file_data["file_list"]["file_date"]

            _path = gen_file_path(_date, UPLOAD_FOLDER, _file_data["tracking_id"])
            _ext = _file_data["file_list"]["file_ext"]
            _file_name = unique_id + _ext

            '''
                with send_file() variant you must initiate submit or have rendered template with url_for()
            '''

            '''_r = make_response(#use this if you want to send smth in headers too
                send_file(
                    path_or_file=_path + "/" + _file_name,
                    mimetype=_file_data["__attachments"][0]["file_content_type"],
                    download_name=_file_data["__attachments"][0]["file_name"],
                    as_attachment=True
                )
            )
            _r.headers['X-Unique-number'] = _file_unique_number
            return _r'''

            '''return send_file(
                path_or_file=_path + "/" + _file_name,
                mimetype=_file_data["file_list"][0]["file_content_type"],
                download_name=_file_data["file_list"][0]["file_name"],
                as_attachment=True
            )'''
            del g.success_handler
            del g.error_handler
            #with this variant we only open the file in the browser and client must download himself
            return send_from_directory(directory=_path, path=_file_name)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Something is wrong with sending file", 400)