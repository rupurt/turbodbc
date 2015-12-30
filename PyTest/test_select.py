from unittest import TestCase

import pydbc


class SelectBaseTestCase(object):
    """
    Children are expected to provide the following attributes:
    
    self.dsn
    self.supports_row_count
    """

    def setUp(self):
        self.connection = pydbc.connect(self.dsn)
        self.cursor = self.connection.cursor()

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def _test_single_row_result_set(self, query, expected_row):
        self.cursor.execute(query)

        if self.supports_row_count:
            self.assertEqual(self.cursor.rowcount, 1)
        else:
            self.assertEqual(self.cursor.rowcount, -1)

        row = self.cursor.fetchone()
        self.assertItemsEqual(row, expected_row)

        row = self.cursor.fetchone()
        self.assertIsNone(row)

    def test_single_row_NULL_result(self):
        self._test_single_row_result_set("SELECT NULL", [None])

    def test_single_row_integer_result(self):
        self._test_single_row_result_set("SELECT 42", [42])

    def test_single_row_string_result(self):
        self._test_single_row_result_set("SELECT 'value'", ["value"])

    def test_single_row_unicode_result(self):
        self._test_single_row_result_set(u"SELECT 'value'", [u"value"])

    def test_single_row_large_numeric_result_as_string(self):
        self._test_single_row_result_set("SELECT -1234567890123.123456789", ['-1234567890123.123456789'])

    def test_single_row_multiple_integer_result(self):
        self._test_single_row_result_set("SELECT 40, 41, 42, 43", [40, 41, 42, 43])

    def test_single_row_double_result(self):
        self.cursor.execute("select a from test_read_double")
        self.assertIn(self.cursor.rowcount, [-1, 1])
        row = self.cursor.fetchone()
        self.assertItemsEqual(row, [3.14])
        row = self.cursor.fetchone()
        self.assertIsNone(row)

    def test_multiple_row_iterate_result(self):
        self.cursor.execute("delete from test_integer")
        for i in xrange(1,10):
            self.cursor.execute("insert into test_integer values("+str(i)+")")
        self.cursor.execute("select * from test_integer order by a")
        for element in enumerate(self.cursor, start=1):
            self.assertItemsEqual([element[0]], element[1])


# Actual test cases

class TestSelectExasol(SelectBaseTestCase, TestCase):
    dsn = "Exasol R&D test database"
    supports_row_count = True
    schema_file = 'db_scripts_exasol.json'


class TestSelectPostgreSQL(SelectBaseTestCase, TestCase):
    dsn = "PostgreSQL R&D test database"
    supports_row_count = False
    schema_file = 'db_scripts_exasol.json'


class TestSelectMySQL(SelectBaseTestCase, TestCase):
    dsn = "MySQL R&D test database"
    supports_row_count = True
    schema_file = 'db_scripts_exasol.json'
