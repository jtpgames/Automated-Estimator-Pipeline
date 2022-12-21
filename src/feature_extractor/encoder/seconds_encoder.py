from sqlalchemy import types


class MilliSecondsEncoder(types.TypeDecorator):
    impl = types.Float

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value * 1000
        return value

    def process_result_value(self, value, dialect):
        return value / 1000
