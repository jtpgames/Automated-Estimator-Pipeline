import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select, MetaData, Table, Column, Integer, String, \
    create_engine

from dto.dtos import DatabaseDTO
from utils import get_date_from_string, does_string_contains_date


class Database:
    def __init__(self, config: DatabaseDTO):
        self.__folder = config.folder
        self.__name = self.__resolve_newest_database(config.name)
        self.__url = self.__get_db_url()
        self.__row_limit = config.row_limit

    def __get_db_url(self):
        db_path = Path(self.__folder)
        Path(db_path).mkdir(parents=True, exist_ok=True)
        full_path = db_path / self.__name
        return "sqlite:///" + full_path.as_posix()

    def write(self, data, cmd_names_mapping):
        logging.info("Start exporting extracted features")
        df_data = pd.DataFrame(data)
        df_mapping = pd.DataFrame.from_dict(
            cmd_names_mapping,
            orient="index",
            columns=["mapping"]
        )

        today = datetime.now().strftime("%Y-%m-%d")
        file_name = "trainingdata_{}.sqlite".format(today)

        # makes sure that folder exists
        db_folder = Path(self.__folder)
        db_folder.mkdir(parents=True, exist_ok=True)
        db_path = db_folder / file_name

        con = create_engine("sqlite:///" + db_path.as_posix())
        df_data.to_sql("gs_training_data", con=con, if_exists="replace")
        df_mapping.to_sql(
            "gs_training_cmd_mapping",
            con=con,
            if_exists="replace"
        )

    def get_cmd_mapping(self, cmd_key=True):
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
            if cmd_key:
                names_mapping_dict[str_cmd] = int_cmd
            else:
                names_mapping_dict[int_cmd] = str_cmd
        return names_mapping_dict

    def get_training_data_cursor_result_columns(self, columns):
        metadata_obj = MetaData()
        data = Table(
            "gs_training_data",
            metadata_obj,
            Column('index', Integer, primary_key=True),
        )
        for col in columns:
            data.append_column(col)
        return self.__execute_query(data, row_limitation=True)

    def get_training_data_cursor_result_column(self, column):
        return self.get_training_data_cursor_result_columns([column])

    def __execute_query(self, table, row_limitation=False):
        engine = create_engine(self.__url)
        con = engine.connect()

        query = select(table)
        if self.__row_limit != -1 and row_limitation:
            query = query.limit(self.__row_limit)
        return con.execute(query)

    def get_date_from_db_name(self):
        return get_date_from_string(self.__name)

    def __resolve_newest_database(self, name) -> str:
        if name != "NEWEST":
            return name

        potential_dbs = Path(self.__folder).glob("*.sqlite")
        name = ""
        files = [x.name for x in potential_dbs if x.is_file() and does_string_contains_date(x.name)]
        if len(files) > 0:
            data = sorted(files, key=get_date_from_string, reverse=True)
            name = data[0]
        else:
            logging.warning("no database exists")
        return name
