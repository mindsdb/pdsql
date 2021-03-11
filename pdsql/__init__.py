import tempfile
import os
import shutil
import time
from pdsql.config import Configuration
from pdsql.exceptions import pdsqlException
from pdsql.data_sources import DataSource


def sql_query(sql, from_tables, *args, **kwargs):
    if not from_tables or not isinstance(from_tables, dict):
        raise pdsqlException(f"Wrong from_tables value. Expected to be a dict of table names and dataframes, got: {str(from_tables)}")

    tmpdir = tempfile.gettempdir() + '/pdsql_temp_' + time.ctime()
    ds = DataSource(*args, metadata_dir=str(tmpdir), **kwargs)
    try:
        for table_name, dataframe in from_tables.items():
            if table_name not in sql:
                raise pdsqlException(f"Table {table_name} found in from_tables, but not in the SQL query.")
            tmp_fpath = os.path.join(tmpdir, f'{table_name}.csv')
            dataframe.to_csv(tmp_fpath, index=False)
            ds.add_table_from_file(tmp_fpath)

        result = ds.query(sql)
        return result
    finally:
        ds.clear_metadata(ds.metadata_dir)
        shutil.rmtree(tmpdir)
