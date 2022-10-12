import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, create_engine, select, String, func


class ModifiedDatabase:
    def __init__(self, number_rows=-1):
        self.number_rows = number_rows
        func.setseed(0.123)

    def get_cmd_mapping(self, cmd_key=True):
        metadata_obj = MetaData()
        query_table = Table(
            'gs_training_cmd_mapping',
            metadata_obj,
            Column('index', String, primary_key=True),
            Column('mapping', Integer)
        )
        query_result = self.execute_query(query_table, data=False)
        names_mapping_dict = {}
        for str_cmd, int_cmd in query_result:
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
        return self.execute_query(data)

    def execute_query(self, table, data=True):
        db_url = r"sqlite:///C:\Users\lierm\IdeaProjects\logfile_analysis\resources\export\db\trainingdata_2022-10-05.sqlite"
        engine = create_engine(db_url)
        con = engine.connect()

        query = select(table)
        if self.number_rows != -1 and data:
            query = query.order_by(func.random()).limit(self.number_rows)
        ret = con.execute(query).all()
        con.close()
        return ret

    def get_df_from_db_column_data(self, db_result, column_names: list):
        column_names.insert(0, "old_index")
        df = pd.DataFrame.from_records(
            db_result,
            # index='index',
            columns=column_names,
            coerce_float=True
        )
        df.drop("old_index", axis=1, inplace=True)
        return df
