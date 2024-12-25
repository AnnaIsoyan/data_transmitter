from flask_restful import Resource
from decorator import monitor_transmitter_header, monitor_transmitter_ip
from flask import Response, g, request
import requests


class SendDataTransmitter(Resource):

    @monitor_transmitter_ip
    @monitor_transmitter_header
    def post(self):
        try:
            redirect_url = request.headers.get('receiver')
            data = request.get_json() if request.is_json else request.form

            request.headers.pop('receiver')
            # request.headers
            try:
                response = requests.post(redirect_url, headers=request.headers, data=data)
                mimetype = response.headers.get('Content-Type', 'text/plain')

                del g.success_handler
                del g.error_handler

                return Response(
                    response.text,
                    status=response.status_code,
                    headers=response.headers,
                    mimetype=mimetype
                )
            except requests.exceptions.Timeout as e:
                g.error_handler.log_to_file(f"Transmitter: Timeout Error - {str(e)}")
                g.error_handler.handle_error(f'Unable to redirect. Timeout error: {e}', 400)
            except requests.RequestException as e:
                g.error_handler.log_to_file(f"Transmitter: RequestException - {str(e)}")
                g.error_handler.handle_error(f'Unable to redirect. RequestException: {e}', 400)
            except (Exception,) as e:
                g.error_handler.log_to_file(f"Transmitter: Exception - {str(e)}")
                g.error_handler.handle_error(f'Unable to redirect. Exception: {e}', 400)

        except (Exception,) as e:
            g.error_handler.log_to_file(str(e))
            g.error_handler.handle_error(f'Unable to redirect. error: {e}', 400)
