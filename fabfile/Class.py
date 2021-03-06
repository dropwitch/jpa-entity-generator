from util import *

import re


class Database:
    def __init__(self, name, persistence_unit_name):
        self.name = name
        self.tables = []
        self.persistence_unit_name = persistence_unit_name
        self.package_name = camel_case(persistence_unit_name).lower()

    def get_name(self):
        return self.name

    def get_tables(self):
        return self.tables

    def add_table(self, table):
        self.tables.append(table)

    def get_persistence_unit_name(self):
        return self.persistence_unit_name

    def get_package_name(self):
        return self.package_name


class Table:
    def __init__(self, name, persistence_unit_name):
        self.name = name
        self.camel_name = camel_case(name)
        self.class_name = pascal_case(name)
        self.columns = []
        self.not_null_columns = []
        self.indices = []
        self.persistence_unit_name = persistence_unit_name
        self.package_name = camel_case(persistence_unit_name).lower()

    def get_name(self):
        return self.name

    def get_class_name(self):
        return self.class_name

    def get_columns(self):
        return self.columns

    def add_column(self, column):
        self.columns.append(column)
        if column.is_not_null() and not column.auto_increment and column.name != "created_at" and column.name != "updated_at":
            self.not_null_columns.append(column)

    def get_indices(self):
        return self.indices

    def add_index(self, index):
        self.indices.append(index)

    def get_persistence_unit_name(self):
        return self.persistence_unit_name

    def get_package_name(self):
        return self.package_name

    def find_column_by_name(self, _column_name):
        for column in self.columns:
            if column.get_name() == _column_name:
                return column
        return None

    def get_primary_key(self):
        for index in self.indices:
            if index.get_type() == "PRIMARY KEY":
                return index

        return None

    def is_primary_key(self, _column):
        index = self.get_primary_key()
        if index:
            for column_name in index.get_column_names():
                if _column.get_name() == column_name:
                    return True

        return False

    def has_composite_primary_keys(self):
        index = self.get_primary_key()
        return index and len(index.get_columns()) > 1


class Index:
    def __init__(self, _type):
        self.column_names = []
        self.columns = []
        self.type = _type

    def get_column_names(self):
        return self.column_names

    def set_column_names(self, _names):
        self.column_names = _names

    def get_columns(self):
        return self.columns

    def add_column(self, _column):
        self.columns.append(_column)

    def get_type(self):
        return self.type

    def get_combined_pascal_column_names(self):
        combined_name = ""
        for column in self.columns:
            combined_name += column.pascal_name
        return combined_name

    def is_composite_pk(self):
        if self.type != "PRIMARY KEY":
            return False

        return len(self.columns) > 1


class Column:
    def __init__(self, _name, _type, _unsigned=None, _not_null=None, _default=None, _auto_increment=None):
        self.name = _name
        self.field_name = camel_case(_name)
        self.pascal_name = pascal_case(_name)
        self.type = _type
        self.field_type = _convert_to_java_type(_type)
        self.field_size = _filter_size(self.field_type, _type)

        self.unsigned = ""
        if _unsigned:
            self.unsigned = _unsigned

        self.not_null = False
        if _not_null == 'NOT NULL':
            self.not_null = True

        self.default = ""
        if _default:
            self.default = _default

        self.auto_increment = ""
        if _auto_increment:
            self.auto_increment = _auto_increment

        self.primary_key = False

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_unsigned(self):
        return self.unsigned

    def is_not_null(self):
        return self.not_null

    def get_default(self):
        return self.default

    def get_auto_increment(self):
        return self.auto_increment

    def is_primary_key(self):
        return self.primary_key

    def set_primary_key(self, _primary_key):
        self.primary_key = _primary_key


def _convert_to_java_type(_type):
    _boolean = re.compile('^tinyint\(1\)', re.IGNORECASE)
    _integer = re.compile('^(tinyint\([23]\)|smallint|mediumint|int)', re.IGNORECASE)
    _long = re.compile('^bigint', re.IGNORECASE)
    _double = re.compile('^double', re.IGNORECASE)
    _string = re.compile('^varchar|^text', re.IGNORECASE)
    _datetime = re.compile('^datetime')
    _timestamp = re.compile('^timestamp')

    if _boolean.match(_type):
        return "boolean"

    if _integer.match(_type):
        return "Integer"

    if _long.match(_type):
        return "Long"

    if _double.match(_type):
        return "Double"

    if _string.match(_type):
        return "String"

    if _datetime.match(_type):
        return "ZonedDateTime"

    if _timestamp.match(_type):
        return "ZonedDateTime"


def _filter_size(_field_type, _type):
    if _field_type == "String":
        match = re.search('\((\d*?)\)', _type)
        if match:
            return match.group(1)

    return None
