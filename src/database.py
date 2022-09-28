import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select, MetaData, Table, Column, Integer, String, \
    create_engine


# TODO better method names, no duplication
class Database:
    def __init__(self, db_export_folder, db_url, db_limit):
        self.__db_export_folder = db_export_folder
        self.__db_url = db_url
        self.__db_limit = db_limit

    def save_features(self, data, cmd_names_mapping):
        logging.info("Start exporting extracted features")
        df_data = pd.DataFrame(data)
        df_mapping = pd.DataFrame.from_dict(
            cmd_names_mapping,
            orient="index",
            columns=["mapping"]
        )

        today = datetime.now().strftime("%Y-%m-%d")
        file_name = "trainingdata_{}.db".format(today)

        # makes sure that folder exists
        db_folder = Path(self.__db_export_folder)
        db_folder.mkdir(parents=True, exist_ok=True)
        db_path = db_folder / file_name

        con = create_engine("sqlite:///" + db_path.as_posix())
        df_data.to_sql("gs_training_data", con=con, if_exists="replace")
        df_mapping.to_sql(
            "gs_training_cmd_mapping",
            con=con,
            if_exists="replace"
        )

    def get_cmd_int_dict(self):
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
            names_mapping_dict[str_cmd] = int_cmd
        return names_mapping_dict

    # TODO refactor to not use duplicated code
    def get_int_cmd_dict(self):
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

    def get_training_data_cursor_result(self, columns):
        metadata_obj = MetaData()
        data = Table(
            "gs_training_data",
            metadata_obj,
            Column('index', Integer, primary_key=True),
        )
        for col in columns:
            data.append_column(col)
        return self.__execute_query(data, row_limitation=True)

    def get_training_data_cursor_result_columns(self, column):
        metadata_obj = MetaData()
        data = Table(
            "gs_training_data",
            metadata_obj,
            Column('index', Integer, primary_key=True),
            column
        )
        return self.__execute_query(data, row_limitation=True)

    def __execute_query(self, table, row_limitation=False):
        engine = create_engine(self.__db_url)
        con = engine.connect()

        query = select(table)
        if self.__db_limit != -1 and row_limitation:
            query = query.limit(self.__db_limit)
        return con.execute(query)
