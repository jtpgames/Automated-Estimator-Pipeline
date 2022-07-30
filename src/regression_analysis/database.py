import pandas as pd
from sqlalchemy import create_engine

from src.regression_analysis.configuration_handler import ConfigurationHandler
from sqlalchemy import select, types, MetaData, Table, Column, Integer, String

class Database:
    def __init__(self, config_handler: ConfigurationHandler):
        self.__db_url = config_handler.get_db_url()
        self.__db_limit = config_handler.get_db_limit()

    def get_names_mapping_from_db(self):
        metadata_obj = MetaData()
        data = Table(
            'gs_training_cmd_mapping',
            metadata_obj,
            Column('index', String, primary_key=True),
            Column('mapping', Integer)
        )
        return self.__execute_query(data)

    def get_training_data_from_db(self, column):
        metadata_obj = MetaData()
        data = Table(
            "gs_training_data",
            metadata_obj,
            Column('index', Integer, primary_key=True),
            column
        )
        return self.__execute_query(data)

    def get_column_from_db_with_encoder(self, table, column, encoder):
        metadata_obj = MetaData()
        data = Table(
            table, metadata_obj,
            Column('index', Integer, primary_key=True),
            Column(column, encoder),
        )
        return self.__execute_query(data)

    def get_column_from_db(self, table, column):
        metadata_obj = MetaData()
        data = Table(
            table, metadata_obj,
            Column('index', Integer, primary_key=True),
            Column(column),
        )
        data.append_column()
        return self.__execute_query(data)

    def __execute_query(self, table):
        engine = create_engine(self.__db_url)
        con = engine.connect()

        query = select(table)
        if self.__db_limit != -1:
            query = query.limit(self.__db_limit)
        return con.execute(query)
