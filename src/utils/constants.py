"""This module contains the constants used in the project."""


class Constants:
    """This class contains the constants used in the project."""
    terminate_text = "TERMINATE"
    maximum_iterations = 15
    execute_select = "execute[SELECT"
    sql_show_tables = "SHOW TABLES"
    sql_show_database = "SHOW DATABASES"
    user_speaker = "user"
    sql_error_message = "Error executing query"
    action_identifier = "Action:"
    observation_identifier = "Observation: "
    action_submit = "submit"
    action_skip = "skip"
    action_skip_response = "skipped"
    init_thought = "Thought: I should first find out what tables are available in this MySQL database that can help me answer this question."
    sqlite_db_file_name = "sql_copilot.sqlite.db"
    default_response = "I'm sorry, I am not able to find any information on that."
    sql_data_manipulation_commands = [
        "UPDATE",
        "DELETE",
        "INSERT",
        "CREATE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "RENAME",
        "START",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        "DECLARE",
        "BEGIN",
        "GRANT",
        "REVOKE",
    ]
