import os
import unittest
from unittest.mock import patch, MagicMock
from src.mysql.execution_env import SqlEnv
from src.utils.constants import Constants

class TestSqlEnv(unittest.TestCase):

    def setUp(self):
        self.config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "database": "test_db",
            "password": "password"
        }
        self.sql_env = SqlEnv(self.config)

    @patch('src.mysql.execution_env.mysql.connector.connect')
    def test_connect(self, mock_connect):
        self.mock_connect = mock_connect
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.sql_env.connect()
        self.mock_connect.assert_called_once_with(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            database=self.config["database"],
            password=self.config["password"]
        )
        self.assertIsNotNone(self.sql_env.cnx)
        self.assertIsNotNone(self.sql_env.cursor)

    @patch('src.mysql.execution_env.mysql.connector.connect')
    def test_execute_action(self, mock_connect):
        self.mock_connect = mock_connect
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.sql_env.connect()
        action = "SELECT * FROM test_table"
        self.mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        self.sql_env.execute_action(action)
        self.mock_cursor.execute.assert_called_once_with(action)
        self.assertEqual(self.sql_env.observation, [("row1",), ("row2",)])
        self.assertTrue(self.sql_env.info["action_executed"])

    @patch('src.mysql.execution_env.mysql.connector.connect')
    def test_step(self, mock_connect):
        self.mock_connect = mock_connect
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.sql_env.connect()
        action = "SELECT * FROM test_table"
        self.mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        observation, reward, done, info = self.sql_env.step(action)
        self.mock_cursor.execute.assert_called_once_with(action)
        self.assertEqual(observation, [("row1",), ("row2",)])
        self.assertEqual(reward, 0)
        self.assertFalse(done)
        self.assertTrue(info["action_executed"])

    def test_reset(self):
        self.sql_env.reset()
        self.assertEqual(self.sql_env.info, {})
        self.assertEqual(self.sql_env.trajectory, [])
        self.assertIsNone(self.sql_env.observation)

    @patch('src.mysql.execution_env.mysql.connector.connect')
    def test_close(self, mock_connect):
        self.mock_connect = mock_connect
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.sql_env.connect()
        self.sql_env.close()
        self.mock_cursor.close.assert_called_once()
        self.mock_connection.close.assert_called_once()

    @patch('src.mysql.execution_env.SqlEnv.get_init_observation')
    def test_attach_init_observation(self, mock_get_init_observation):
        mock_get_init_observation.return_value = "Initial Observation"
        query = "SELECT * FROM test_table"
        result = self.sql_env.attach_init_observation(query)
        expected_result = f"Question: {query}\n{Constants.init_thought}\nAction: execute[{Constants.sql_show_tables}]\nObservation: Initial Observation"
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
