"""This module contains the class SqlEnv which is used to interact with the MySQL database."""
from typing import Dict, Tuple, Any
import os
import mysql.connector
from src.utils.constants import Constants


class SqlEnv:
    """This class is used to interact with the MySQL database."""
    SQL_CONFIG = {
        "host": os.getenv("MYSQL_HOST", None),
        "port": os.getenv("MYSQL_PORT", None),
        "user": os.getenv("MYSQL_USER", None),
        "database": os.getenv("MYSQL_DATABASE", None),
        "password": os.getenv("MYSQL_PASSWORD", None),
    }
    initial_observation = None

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initializes the class with the given configuration.
        
        Args:
            config (dict): A dictionary containing the configuration details.
        """
        self.config = config
        self.cnx = None
        self.cursor = None
        self.observation = None
        self.info = {}
        self.trajectory = []

    def connect(self) -> None:
        """Connects to the MySQL database."""
        self.cnx = mysql.connector.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            database=self.config["database"],
            password=self.config["password"],
        )
        self.cursor = self.cnx.cursor(buffered=True)

    def execute_action(self, action) -> None:
        """
        Executes the given action.
        
        Args:
            action (str): The action to be executed.
        """
        try:
            if not self.cnx or not self.cnx.is_connected():
                self.connect()
            self.cursor.execute(action)
            if self.cursor.description is not None:
                self.observation = self.cursor.fetchall()
            self.info["action_executed"] = True
        except Exception as err: # pylint: disable=broad-except
            self.observation = f"{Constants.sql_error_message}: {err.msg}"
            self.info["error"] = err

    def step(self, action: str) -> Tuple[str, int, bool, Dict]:
        """
        Takes a step in the environment by executing the given action.
        
        Args:
            action (str): The action to be executed.
            
        Returns:
            Tuple[str, int, bool, Dict]: A tuple containing the observation, reward, done, and info.
        """
        if action == Constants.action_skip:
            return Constants.action_skip_response, 0, True, {}
        if action.startswith(Constants.action_submit):
            self.trajectory.append((action, None))
            reward, info = 0, {}
            info["action_executed"] = True
            return self.observation, reward, True, info

        self.execute_action(action)
        self.trajectory.append((action, self.observation))
        return self.observation, 0, False, self.info

    def reset(self):
        """Resets the environment."""
        self.info = {}
        self.trajectory = []
        self.observation = None

    def close(self) -> None:
        """Closes the connection to the MySQL database."""
        self.cursor.close()
        self.cnx.close()

    def get_init_observation(self) -> str:
        """
        Returns the initial observation.
        
        Returns:
            str: The initial observation.
        """
        if self.initial_observation is None:
            self.initial_observation, _, _, _ = self.step(Constants.sql_show_tables)
        return self.initial_observation

    def attach_init_observation(self, query: str) -> str:
        """
        Attaches the initial observation to the given query.
        
        Args:
            query (str): The query to which the initial observation is to be attached.
            
        Returns:
            str: The query with the initial observation attached.
        """
        return f"Question: {query}\n{Constants.init_thought}\nAction: execute[{Constants.sql_show_tables}]\nObservation: {self.get_init_observation()}"

    @staticmethod
    def get_sql_executor_env_from_environment() -> "SqlEnv":
        """
        Returns an instance of the SqlEnv class with the configuration details from the environment.
        
        Returns:
            SqlEnv: An instance of the SqlEnv class.
        """
        return SqlEnv(SqlEnv.SQL_CONFIG)
