from itertools import islice
from enum import Enum
import csv, sys
import copy
import abc
import numpy as np


class Schema(object):
    separator = ','

    def __init__(self, csv_file_path, header=False, separator=None):
        self._csv_file_path = csv_file_path
        if separator is not None:
            tseparator = separator.strip()
            if len(tseparator) < 0 or len(tseparator) > 1:
                raise Exception('Invalid separator [%s]' % separator)
            self.separator = tseparator
        header_row = [col.strip() for col in Schema._read_n_rows(self._csv_file_path, 1, sep=self.separator)[0]]
        if header:
            duplicates = set([x for x in header_row if header_row.count(x) > 1])
            if len(duplicates) > 0:
                raise Exception("Should be no duplicates in CSV header: " + ", ".join([col for col in duplicates]))
            self._columns = [BasicColumn(item, [index], BasicColumn.Type.STRING) for index, item in enumerate(header_row)]
        else:
            self._columns = [BasicColumn('col_' + str(index), [index], BasicColumn.Type.STRING) for index in range(0, len(header_row))]

    @property
    def csv_file_path(self):
        return self._csv_file_path

    @staticmethod
    def _read_n_rows(csv_file_path, rows_number, sep=','):
        rows = []
        with open(csv_file_path, 'rb') as f:
            reader = csv.reader(f, delimiter=sep)
            try:
                for row in islice(reader, 0, rows_number):
                    rows.append(row)
            except csv.Error as e:
                sys.exit('Broken line: file %s, line %d: %s' % (csv_file_path, reader.line_num, e))

        return rows

    def __setitem__(self, old_name, new_name):
        columns = [c.name for c in self._columns]
        if old_name != new_name and columns.count(new_name) > 0:
            raise Exception("Should be no duplicates in columns: " + new_name)
        for column in self._columns:
            if column.name == old_name:
                column.name = new_name.strip()

    @property
    def columns(self):
        return self._columns

    def update_columns(self, columns):
        self._columns = columns

    @columns.setter
    def columns(self, columns):
        l = len(columns)
        if (l > len(self._columns)) or (l < len(self._columns)):
            raise Exception("Passed columns number: %d is not compatible with Schema current columns number: %d"
                            % (l, len(self._columns)))
        duplicates = set([x for x in columns if columns.count(x) > 1])
        if len(duplicates) > 0:
            raise Exception("Should be no duplicates in columns: " + ", ".join([col for col in duplicates]))
        for index, item in enumerate(columns):
            self._columns[index].name = item.strip()

    def drop_column(self, column_name):
        for index, column in enumerate(copy.deepcopy(self._columns)):
            if column.name == column_name:
                self._columns.remove(self._columns[index])

    def merge_columns(self, new_column_name, columns_to_merge):
        if not isinstance(columns_to_merge, list):
            raise TypeError("Arg columns_to_merge should be list")
        columns_indexes = []
        for column in copy.deepcopy(self._columns):
            if column.name in columns_to_merge:
                columns_indexes.extend(column.columns_indexes)
                self.drop_column(column.name)
        self._columns.append(BasicColumn(new_column_name, columns_indexes))

    def merge_columns_in_range(self, new_column_name, range=()):
        if not isinstance(range, tuple):
            raise TypeError("Arg range should be Tuple")
        if range[0] >= range[1]:
            raise Exception("Start index of the range can't be higher or equal than end index")
        if range[0] < 0 or range[1] >= len(self._columns):
            raise Exception("Range is out of length of schema, last schema index: %d" % (len(self._columns) - 1))
        columns_indexes = []
        for index, column in enumerate(copy.deepcopy(self._columns)):
            if range[0] <= index <= range[1]:
                columns_indexes.extend(column.columns_indexes)
                self.drop_column(column.name)
        self._columns.append(BasicColumn(new_column_name, columns_indexes))

    def print_columns(self):
        print ", ".join([col.name for col in self._columns])

    def print_data(self):
        print "First 10 records:"
        for row in Schema._read_n_rows(self.csv_file_path, 10):
            print row


class Input(object):
    def __init__(self, schema=None):
        if schema is not None and not isinstance(schema, Schema):
            raise TypeError("Pass Schema instance as an argument")
        self._schema = schema

    @property
    def schema(self):
        return self._schema

    class Builder(object):
        def __init__(self, schema_config):
            self._schema_config = schema_config

        def build(self):
            from img2d import Img2DColumn
            config = self._schema_config
            schema = Schema(config['csv_file_path'], config['header'], config['separator'])
            config_columns = config['columns']
            columns_indexes_number = sum(len(column["index"]) for column in config_columns)
            if columns_indexes_number != len(schema.columns):
                raise TypeError("Columns indexes number in config is not equal to csv file: %s" % columns_indexes_number)

            result_columns = []
            for index, config_column in enumerate(config_columns):
                column_type = config_column['type']
                if column_type in BasicColumn.type():
                    result_columns.append(BasicColumn(config_column['name'], config_column['index'], column_type))
                elif column_type == Img2DColumn.type():
                    result_columns.append(Img2DColumn.Builder(config_column).build())
                else:
                    raise TypeError("Unsupported column type: %s" % column_type)
            schema.update_columns(result_columns)
            return Input(schema)

    def add_int_column(self, column_name):
        _, column = self._find_column_in_schema(column_name)
        column.data_type = BasicColumn.Type.INT

    def add_float_column(self, column_name):
        _, column = self._find_column_in_schema(column_name)
        column.data_type = BasicColumn.Type.FLOAT

    def add_categorical_column(self, column_name):
        _, column = self._find_column_in_schema(column_name)
        column.data_type = BasicColumn.Type.CATEGORICAL
        column.metadata = set()

    def add_string_column(self, column_name):
        _, column = self._find_column_in_schema(column_name)
        column.data_type = BasicColumn.Type.STRING

    def add_vector_column(self, column_name):
        _, column = self._find_column_in_schema(column_name)
        column.data_type = BasicColumn.Type.VECTOR

    def add_column(self, column_name, input_column):
        index, column = self._find_column_in_schema(column_name)
        input_column.name = column_name
        input_column.columns_indexes = column.columns_indexes
        self._schema.columns[index] = input_column

    def _find_column_in_schema(self, column_name):
        for index, schema_column in enumerate(self._schema.columns):
            if schema_column.name == column_name:
                return index, schema_column
        raise Exception("No column with name %s in schema." % (column_name))


class Column(object):
    def __init__(self, name=None, columns_indexes=[], data_type=None, reader=None, ser_de=None):
        self._name = name
        # CSV corresponding columns indexes
        self._columns_indexes = columns_indexes
        self._data_type = data_type
        self._reader = reader
        self._ser_de = ser_de

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def columns_indexes(self):
        return self._columns_indexes

    @columns_indexes.setter
    def columns_indexes(self, columns_indexes):
        self._columns_indexes = columns_indexes

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        self._data_type = data_type

    @property
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, reader):
        self._reader = reader

    @property
    def ser_de(self):
        return self._ser_de

    @ser_de.setter
    def ser_de(self, ser_de):
        self._ser_de = ser_de

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata


class ComplexColumn(Column):
    def __init__(self, data_type=None, pre_transforms=None, post_transforms=None, ser_de=None, reader=None):
        super(ComplexColumn, self).__init__(data_type=data_type)
        self._pre_transforms = pre_transforms
        self._post_transforms = post_transforms

    @property
    def pre_transforms(self):
        return self._pre_transforms

    @pre_transforms.setter
    def pre_transforms(self, pre_transforms):
        self._pre_transforms = pre_transforms

    @property
    def post_transforms(self):
        return self._post_transforms

    @post_transforms.setter
    def post_transforms(self, post_transforms):
        self._post_transforms = post_transforms


class ColumnTransform(object):
    def __init__(self):
        pass

    @staticmethod
    def type():
        pass

    def apply(self, data):
        return data


class ColumnReader(object):
    def __init__(self, column):
        self._column = column

    @abc.abstractmethod
    def read(self, csv_row):
        pass


class ColumnSerDe(object):

    @abc.abstractmethod
    def serialize(self, data):
        pass

    @abc.abstractmethod
    def deserialize(self, path):
        pass


class BasicColumn(Column):
    def __init__(self, name=None, columns_indexes=[], data_type=None, reader=None, ser_de=None):
        super(BasicColumn, self).__init__(name, columns_indexes, data_type, reader, ser_de)
        self.reader = BasicColumnReader(self)
        self.ser_de = BasicColumnSerDe(data_type)

    class Type(Enum):
        INT = "INT"
        FLOAT = "FLOAT"
        STRING = "STRING"
        VECTOR = "VECTOR"
        CATEGORICAL = "CATEGORICAL"

    @staticmethod
    def type():
        return [BasicColumn.Type.INT,
                BasicColumn.Type.FLOAT,
                BasicColumn.Type.STRING,
                BasicColumn.Type.VECTOR,
                BasicColumn.Type.CATEGORICAL]


class BasicColumnReader(ColumnReader):
    def read(self, csv_row):
        if self._column.data_type == BasicColumn.Type.STRING:
            return csv_row[self._column.columns_indexes[0]]
        if self._column.data_type == BasicColumn.Type.INT:
            return csv_row[self._column.columns_indexes[0]]
        if self._column.data_type == BasicColumn.Type.FLOAT:
            return csv_row[self._column.columns_indexes[0]]
        if self._column.data_type == BasicColumn.Type.VECTOR:
            return [float(csv_row[i]) for i in self._column.columns_indexes]
        if self._column.data_type == BasicColumn.Type.CATEGORICAL:
            cat_val = csv_row[self._column.columns_indexes[0]]
            cat_val_idx = list(self._column.metadata).index(cat_val)
            return cat_val_idx


class BasicColumnSerDe(ColumnSerDe):
    def __init__(self, data_type):
        self._data_type = data_type

    def serialize(self, data):
        if self._data_type == BasicColumn.Type.STRING:
            return str(data)
        if self._data_type == BasicColumn.Type.INT:
            return int(data)
        if self._data_type == BasicColumn.Type.FLOAT:
            return float(data)
        if self._data_type == BasicColumn.Type.VECTOR:
            return np.array(data)
        if self._data_type == BasicColumn.Type.CATEGORICAL:
            return int(data)

    @abc.abstractmethod
    def deserialize(self, path):
        pass