from flask_restx import Namespace, Resource, fields, reqparse, inputs
from lib.logging import BasicErrorHandler, APIErrorHandler
from lib.utils import load_err_messages, load_help_messages
from lib.exceptions import PageOutofBoundsError
from flask_restx.errors import HTTPException
from datetime import datetime
from model import FinancialData, FinancialDataSerializer
from financial.list_financial_data import main as list_financial_data
from financial.get_statistics import main as get_statistics
from math import ceil
from flask_restx.errors import ValidationError
from random import randint as rint, random as rfloat
from conf.settings import DEFAULT_DATE_FMT, FIXTURES_DIR
from pathlib import Path
import json


help_messages = load_help_messages()["api"]
err_messages = load_err_messages()
api = Namespace("financial_api", help_messages["desc"], path="/")

INFO_BASE_RESPONSE = api.model('ExtraInformation', {
    'info': fields.Nested(
                api.model("ErrorMessage", {
                    "error": fields.String(required=True, default='', example='')
                })
            )
})

PAGINATION_BASE_RESPONSE = api.model('Pagination', {
    'count': fields.Integer(required=True),
    'page': fields.Integer(required=True),
    'limit': fields.Integer(required=True),
    'pages': fields.Integer(required=True)
})


class EmptyContentException(HTTPException):
    code = 404


@api.route('/financial_data', methods=['GET'])
class FinancialDataView(Resource):
    RESPONSE = api.inherit('Response::ListFinancialData', INFO_BASE_RESPONSE, {
        'data': fields.Nested(
            api.model("Model::FinancialDataSummary", {
                "symbol": fields.String(example=FinancialData.Symbols.as_set(codes_only=True).pop()),
                "date": fields.Date(example=datetime.now().strftime(DEFAULT_DATE_FMT)),
                "open_price": fields.Float(example=rfloat()*100//1),
                "close_price": fields.Float(example=rfloat()*100//1),
                "volume": fields.Integer(example=rint(1, 100))
            }, as_list=True),
            allow_null=True),
        'pagination': fields.Nested(PAGINATION_BASE_RESPONSE, allow_null=True)
    })

    REQUEST = reqparse.RequestParser()
    REQUEST.add_argument('start_date', type=inputs.date, location='args', help=help_messages["fields"]["date"], store_missing=False)
    REQUEST.add_argument('end_date', type=inputs.date, location='args', help=help_messages["fields"]["date"], store_missing=False)
    REQUEST.add_argument('symbol', choices=list(FinancialData.Symbols.as_set(codes_only=True)), type=str, location='args', store_missing=False)
    REQUEST.add_argument('limit', type=inputs.int_range(1, 10000), location='args', default=5)
    REQUEST.add_argument('page', type=inputs.int_range(1, 10000), location='args', default=1)

    @api.marshal_with(RESPONSE, description=help_messages["ok_resp"])
    @api.expect(REQUEST, validate=True)
    # Catch any error that is not handled so far, and return 500 error, with a preset message.
    @APIErrorHandler('FinancialDataView', BaseException, 500, err_messages["api"]["E500"])
    # Catch ValidationErrors and return 400 status code, and pass the message of the original exception to client-side.
    @APIErrorHandler('FinancialDataView', ValidationError, 400)
    @APIErrorHandler('FinancialDataView', PageOutofBoundsError, 400)
    # Handle Empty Content Result
    @APIErrorHandler('FinancialDataView', EmptyContentException, 404, err_messages["api"]["E404_no_content"])
    def get(self):
        kwargs = self.REQUEST.parse_args()
        self._validate_get_inputs(kwargs)
        total, arr = list_financial_data(**kwargs)
        if total == 0:
            raise EmptyContentException
        return {
            "data": FinancialDataSerializer.serialize(arr, exclude=["id", "created_at", "updated_at"]),
            "pagination": {
                "count": total,
                "page": kwargs["page"],
                "limit": kwargs["limit"],
                "pages": ceil(float(total)/kwargs["limit"])
            }
        }

    @BasicErrorHandler('FinancialDataGetValidator', expectedErrClass=ValidationError, rethrow_as=ValidationError)
    def _validate_get_inputs(self, kwargs):
        if 'end_date' in kwargs and 'start_date' in kwargs:
            if kwargs["end_date"] < kwargs["start_date"]:
                raise ValidationError(err_messages["api"]["end<start"])


@api.route('/statistics', methods=['GET'])
class StatisticsView(Resource):
    RESPONSE = api.inherit('Response::GetStatistics', INFO_BASE_RESPONSE, {
        'data': fields.Nested(
            api.model("Model::StatisticsDataSummary", {
                "start_date": fields.Date(example=datetime.now().strftime(DEFAULT_DATE_FMT)),
                "end_date": fields.Date(example=datetime.now().strftime(DEFAULT_DATE_FMT)),
                "symbol": fields.String(example=FinancialData.Symbols.as_set(codes_only=True).pop()),
                "average_daily_open_price": fields.Float(rfloat()*100//1),
                "average_daily_close_price": fields.Float(rfloat()*100//1),
                "average_daily_volume": fields.Integer(rint(1, 100))
            }),
            allow_null=True)
    })

    REQUEST = reqparse.RequestParser()
    REQUEST.add_argument('start_date', type=inputs.date, location='args', help=help_messages["fields"]["date"], required=True)
    REQUEST.add_argument('end_date', type=inputs.date, location='args', help=help_messages["fields"]["date"], required=True)
    REQUEST.add_argument('symbol', choices=list(FinancialData.Symbols.as_set(codes_only=True)), type=str, location='args', required=True)

    @api.marshal_with(RESPONSE, description=help_messages["ok_resp"])
    @api.expect(REQUEST, validate=True)
    # Catch any error that is not handled so far, and return 500 error, with a preset message.
    @APIErrorHandler('StatisticsView', BaseException, 500, err_messages["api"]["E500"])
    # Catch ValidationErrors and return 400 status code, and pass the message of the original exception to client-side.
    @APIErrorHandler('StatisticsView', ValidationError, 400)
    # Handle Empty Content Result
    @APIErrorHandler('StatisticsView', EmptyContentException, 404, err_messages["api"]["E404_no_content"])
    def get(self):
        kwargs = self.REQUEST.parse_args()
        self._validate_get_inputs(kwargs)
        data = get_statistics(**kwargs)
        if not data:
            raise EmptyContentException
        data.update(**kwargs)
        return {
            "data": data
        }

    @BasicErrorHandler('StatisticsGetValidator', expectedErrClass=ValidationError, rethrow_as=ValidationError)
    def _validate_get_inputs(self, kwargs):
        if kwargs["end_date"] < kwargs["start_date"]:
            raise ValidationError(err_messages["api"]["end<start"])
        if kwargs["symbol"] not in FinancialData.Symbols.as_set(codes_only=True):
            raise ValidationError(err_messages["api"]["symb_undefined"])
