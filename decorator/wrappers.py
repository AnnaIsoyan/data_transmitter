from handler import save_mulberry_api_log
from cfg import NOT_ALLOWED_EXTENSIONS, SINGLE_FILE_MAX_SIZE, TOTAL_FILE_MAX_SIZE, is_allowed_ip, \
    EXTERNAL_SOURCE_TRANSMITTER_ALLOWED_IP_LIST
from functools import wraps
from flask import request, abort, g
import json
import mimetypes
import magic
import uuid
import zipfile

'''def not_handled_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(f'not handled error occurred: {str(e)}')
            g.error_handler.handle_error('Something went wrong on the server', 500)

    return wrapper'''


def save_data_preprocessed(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            ip = request.environ['REMOTE_ADDR'] \
                if request.environ.get('HTTP_X_FORWARDED_FOR') is None \
                else request.environ['HTTP_X_FORWARDED_FOR']  # behind a proxy

            if request.mimetype != 'multipart/form-data' or not request.form:
                msg = f'got bad request: ip {ip}, mimetype: {request.mimetype}'
                g.error_handler.log_to_file(msg)

                return

            data = json.loads(request.form.to_dict()['data'])
            _data = {
                'data': data,
                'ip': ip
            }
            save_mulberry_api_log(_data)

            return function(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def validate_ip():
    ip = request.environ['REMOTE_ADDR'] \
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None \
        else request.environ['HTTP_X_FORWARDED_FOR']  # behind a proxy
    if not is_allowed_ip(ip):
        msg = f'Invalid IP address: {ip}'
        g.error_handler.log_to_file(msg)
        # unauthorized access
        g.error_handler.handle_error(msg, 401)


def validate_transmitter_ip():
    ip = request.environ['REMOTE_ADDR'] \
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None \
        else request.environ['HTTP_X_FORWARDED_FOR']  # behind a proxy
    if ip not in MULBERRY_TRANSMITTER_ALLOWED_IP_LIST:
        msg = f'Invalid IP address: {ip}'
        g.error_handler.log_to_file(msg)
        # unauthorized access
        g.error_handler.handle_error(msg, 401)


# the function will be called after response
# do not use this is only an example
'''def monitor_ip(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
       
        _ = function(*args, **kwargs)
        validate_ip()
        return _
    return wrapper'''


def monitor_ip(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            validate_ip()
            return function(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def monitor_transmitter_ip(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            validate_transmitter_ip()
            return function(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def monitor_transmitter_header(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if 'receiver' not in request.headers:
                msg = 'receiver is missing'
                g.error_handler.log_to_file(msg)
                g.error_handler.handle_error(msg, 400)
            return function(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def monitor_header(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            headers = ['Header1', 'Header2', 'Header3']
            for header in headers:
                if header not in request.headers:
                    msg = f'Missing header: {header}'
                    g.error_handler.log_to_file(msg)
                    abort(400, msg)
            return func(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def validate_data():
    if request.mimetype != 'multipart/form-data':
        msg = f'Request type must be multipart/form-data. it is {request.mimetype} instead'
        g.error_handler.log_to_file(msg)
        g.error_handler.handle_error(msg, 400)
    r = request.form.to_dict()
    if not request.form or not 'data' in r:
        msg = f'Empty request body given'
        g.error_handler.log_to_file(msg)
        g.error_handler.handle_error(msg, 400)

    data = json.loads(r['data'])
    if not data:
        msg = 'Data is missing'
        g.error_handler.log_to_file(msg)
        g.error_handler.handle_error(msg, 400)


def monitor_data(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            validate_data()
            return func(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper


def validate_params(params, data):
    for param in params.keys():
        is_required = params[param]['is_required'] if 'is_required' in params[param] else False
        _t = get_param_type(params[param]["type"])
        if is_required:
            if param not in data:
                msg = f'Missing parameter: {param}'
                g.error_handler.log_to_file(msg)
                g.error_handler.handle_error(msg, 400)
            if not isinstance(data[param], _t):
                msg = f'Wrong parameter type: {param}'
                g.error_handler.log_to_file(msg)
                g.error_handler.handle_error(msg, 400)

        if "properties" in params[param] and param in data and bool(data[param]):
            if _t == dict:
                validate_params(params[param]['properties'], data[param])
            elif _t == list:
                for l in data[param]:
                    validate_params(params[param]['properties'], l)


def get_param_type(t):
    if t == "list":
        return list
    elif t == "dict":
        return dict
    else:
        return str


def monitor_params(params):
    def decorator(func=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                r = request.form.to_dict()
                data = json.loads(r['data'])
                validate_params(params, data)

                return func(*args, **kwargs)
            except (Exception,) as e:
                g.error_handler.log_to_file(str(e))
                g.error_handler.handle_error("Unknown Error", 500)

        return wrapper

    return decorator


def validate_file(f_list, f_name_list):
    if len(f_list) != len(f_name_list):
        msg = f'request is incomplete. Some files contents are not received'
        g.error_handler.log_to_file(msg)
        g.error_handler.handle_error(msg, 400)

    total_size = 0
    for file_name in f_name_list:
        if file_name not in f_list:
            msg = f'request is incomplete. No file content for {file_name}'
            g.error_handler.log_to_file(msg)
            g.error_handler.handle_error(msg, 400)
        file_data = f_list.getlist(file_name)[0]
        # _mimetype = str(file_data.headers.get("Content-Type"))
        f = magic.Magic(mime=True)
        _stream = file_data.stream.read()
        _mimetype = f.from_buffer(_stream)

        if _mimetype == "application/zip":
            try:
                with zipfile.ZipFile(_stream) as zip_ref:
                    if "word/document.xml" in zip_ref.namelist():
                        _mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:
                        _mimetype = "application/zip"
            except zipfile.BadZipFile:
                msg = f'file is not correct, filename: {file_name}, mimetype: {_mimetype}'
                g.error_handler.log_to_file(msg)
                g.error_handler.handle_error(msg, 400)

        _uuid = str(uuid.uuid4()).replace('-', '')
        _file_original_name = file_data.filename
        _ext = mimetypes.guess_extension(type=_mimetype, strict=False)
        _original_ext = _file_original_name.rsplit(".", 1)[-1]
        _file_name = _uuid + _ext if _ext == _original_ext else _original_ext

        # open file stream, read and pass to the magic library
        # save file stream data to the global to read then in file_util

        # change filename of stream file object
        file_data.filename = _file_name

        # calc content length
        file_data.stream.seek(0, 2)
        _content_length = file_data.stream.tell()
        file_data.stream.seek(0, 0)

        # close file stream
        # file_data.stream.close()

        g.__setattr__(file_name, {
            "_file_original_name": _file_original_name,
            "_mimetype": _mimetype,
            "_uuid": _uuid,
            "_ext": _ext,
            "_file_name": _file_name,
            "_content_length": _content_length
        })

        # file_name = secure_filename(file_data.filename)#this deleted armenian characters
        # mulberry is uzbec, has no appropriate mimetype
        # _mimetype = file_data.content_type if 'content_type' in file_data and file_data['content_type'] else file_data.mimetype
        # _mimetype = save_file_object_api_log(file_data)

        if _ext is None or not bool(_ext):
            msg = f'unable to guess the file extension. file_name {_file_original_name}, mimetype: {_mimetype}'
            g.error_handler.log_to_file(msg)
            g.error_handler.handle_error(msg, 400)
        if _ext in NOT_ALLOWED_EXTENSIONS:
            msg = f'Bad request. Not allowed file type given. file_name {_file_original_name}, type: {_mimetype}'
            g.error_handler.log_to_file(msg)
            g.error_handler.handle_error(msg, 400)

        if _content_length > SINGLE_FILE_MAX_SIZE:
            msg = f'Single file max size exceeds. file_name {_file_original_name}, type: {_mimetype}, size: {_content_length}'
            g.error_handler.log_to_file(msg)
            g.error_handler.handle_error(msg, 400)

        total_size += _content_length

    if total_size > TOTAL_FILE_MAX_SIZE:
        msg = f'Total file max size exceeds. Total size calculated: {total_size}'
        g.error_handler.log_to_file(msg)
        g.error_handler.handle_error(msg, 400)


def monitor_files(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = json.loads(request.form.to_dict()['data'])
            attached = data["__attachments"] if "__attachments" in data else []
            if bool(attached):
                f_name_list = [attachment['name'] for attachment in attached]
                f_list = request.files

                validate_file(f_list, f_name_list)

            return func(*args, **kwargs)
        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error("Unknown Error", 500)

    return wrapper
