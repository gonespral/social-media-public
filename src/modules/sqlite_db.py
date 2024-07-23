"""
Relational database module
"""

import sqlite3


class Database:
    def __init__(self, db_file_path):
        """
        Create a new database connection
        :param db_file_path: Location of the database file
        """
        self.conn = sqlite3.connect(db_file_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def create_table(self, table_name: str, fields: list[str]):
        """
        Create a new table
        :param table_name: Name of the table
        :param fields: Fields of the table
        :return:
        """
        fields = ", ".join([f'"{field}"' for field in fields])
        table_name = f'"{table_name}"'
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} ({})
        '''.format(table_name, fields))
        self.conn.commit()

    def drop_table(self, table_name: str):
        """
        Drop a table
        :param table_name: Name of the table
        :return:
        """
        table_name = f'"{table_name}"'
        self.cursor.execute('''
            DROP TABLE IF EXISTS {}
        '''.format(table_name))
        self.conn.commit()

    def list_tables(self):
        """
        List all tables in the database
        :return: List of tables
        """
        self.cursor.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        ''')
        res = self.cursor.fetchall()
        res_flattened = [x[0] for x in res]
        return res_flattened

    def insert(self, table_name: str, fields: list[str], values: list[str], unique: bool = True):
        """
        Insert a new row into a table
        :param table_name: Name of the table
        :param fields: Fields of the table
        :param values: Values to insert
        :param unique: If True, insert only if row does not exist
        :return:
        """
        fields = ", ".join([f'"{field}"' for field in fields])
        values = ", ".join([f'"{value}"' for value in values])
        if unique:
            self.cursor.execute('''
                INSERT OR IGNORE INTO {} ({})
                VALUES ({})
            '''.format(table_name, fields, values))
        else:
            self.cursor.execute('''
                INSERT INTO {} ({})
                VALUES ({})
            '''.format(table_name, fields, values))

    def update(self, table_name: str, fields: list[str], values: list[str], where: str = None):
        """
        Update rows in a table. If where clause returns no rows, insert a new row.
        :param table_name: Name of the table
        :param fields: Fields to update
        :param values: Values to update
        :param where: Where clause
        :return:
        """
        fields_ = ", ".join([f'"{field}"' for field in fields])
        values_ = ", ".join([f'"{value}"' for value in values])
        if where:
            where = f'WHERE {where}'
        self.cursor.execute('''
            UPDATE {}
            SET ({}) = ({})
            {}
        '''.format(table_name, fields_, values_, where))
        if self.cursor.rowcount == 0:
            self.insert(table_name, fields, values)
        self.conn.commit()

    def select(self, table_name: str, fields: str, where: str = None, return_dict: bool = True):
        """
        Select rows from a table
        :param table_name: Name of the table
        :param fields: Fields to select
        :param where: Where clause
        :param return_dict: If True, return a list of dicts. If False, return a list of rows.
        :return: List of rows
        """
        table_name = f'"{table_name}"'
        if where:
            where = f'WHERE {where}'
        self.cursor.execute('''
            SELECT {} FROM {}
            {}
        '''.format(fields, table_name, where))
        if return_dict:
            rows = self.cursor.fetchall()
            return [dict(zip([x[0] for x in self.cursor.description], row)) for row in rows]
        else:
            return self.cursor.fetchall()

    def delete(self, table_name: str, where: str = None):
        """
        Delete rows from a table
        :param table_name: Name of the table
        :param where: Where clause
        :return:
        """
        table_name = f'"{table_name}"'
        if where:
            where = f'WHERE {where}'
        self.cursor.execute('''
            DELETE FROM {}
            {}
        '''.format(table_name, where))
        self.conn.commit()
