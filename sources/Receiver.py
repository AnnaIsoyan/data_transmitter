from flask_restful import Resource
from flask import Response, g
from decorator import monitor_ip, monitor_data, monitor_params,\
    monitor_files, save_data_preprocessed
from cfg import DATA_PARAM_LIST
from operation import CreateData

class ReceiveDataTransmitter(Resource):

    @save_data_preprocessed
    @monitor_ip
    @monitor_data
    @monitor_params(DATA_PARAM_LIST)
    @monitor_files
    def post(self):
        try:
            mr = CreateData()
            mr.create()
            msg = mr.get_msg()
            del g.success_handler
            del g.error_handler
            return Response(msg, mimetype="text/plain; charset=UTF-8")
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error('Something is wrong with the request', 400)