from ast import literal_eval

from sqlalchemy import types
import json


class JSONEncodedDict(types.TypeDecorator):
    impl = types.TEXT

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        return literal_eval(value)