from flask_restful import Resource
from flask import Response

class HealthCheck(Resource):
    def get(self):
        return Response("The birds are flying by", mimetype="text/text")
