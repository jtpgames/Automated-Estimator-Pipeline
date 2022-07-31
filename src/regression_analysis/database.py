from src.regression_analysis.configuration_handler import ConfigurationHandler
from sqlalchemy import select, types, MetaData, Table, Column, Integer, String, \
    create_engine


class Database:
    def __init__(self, config_handler: ConfigurationHandler):
        self.__db_url = config_handler.get_db_url()
        self.__db_limit = config_handler.get_db_limit()

    def get_cmd_names_dict(self):
        metadata_obj = MetaData()
        query_table = Table(
            'gs_training_cmd_mapping',
            metadata_obj,
            Column('index', String, primary_key=True),
            Column('mapping', Integer)
        )
        query_result = self.__execute_query(query_table)
        names_mapping_dict = {}
        for str_cmd, int_cmd in query_result.all():
            names_mapping_dict[int_cmd] = str_cmd
        return names_mapping_dict

    def get_training_data_from_db(self, column):
        metadata_obj = MetaData()
        data = Table(
            "gs_training_data",
            metadata_obj,
            Column('index', Integer, primary_key=True),
            column
        )
        return self.__execute_query(data)

    def __execute_query(self, table):
        engine = create_engine(self.__db_url)
        con = engine.connect()

        query = select(table)
        if self.__db_limit != -1:
            query = query.limit(self.__db_limit)
        return con.execute(query)
