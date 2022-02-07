import os
from flask import Response, abort
from flask_restplus import Namespace, Resource, fields

api = Namespace('data_pre', description='格式化資料')

payload = api.model('controller_data_pre_payload', {
    'pre_policy': fields.List(fields.Url(description='處理格式選項')),
    'input_file_path': fields.String(requried=True, default='./data/example...', description='輸入資料路徑'),
    'output_file_path': fields.String(requried=True, default='./data/example...', description='輸出資料路徑'),
})


class ControllerPre:
    def __init__(self, input_payload):
        pass


@api.route('/', endpoint='data_pre')
class DataPre(Resource):
    @api.doc(body=payload)
    @api.expect(fields=payload, validate=True)
    def post(self):
        payload_data = api.payload
        # payload_data = json.loads(payload_data)
        print(payload_data)
        if isinstance(payload_data, dict):
            try:
                controller = ControllerPre(payload_data)
            except:
                abort(400, 'Bad Request')
            else:
                try:
                    controller.process()
                    return controller.__str__()
                except:
                    abort(500)
