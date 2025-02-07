import os
from sqlalchemy import create_engine, text

from chainlit.data.storage_clients.base import BaseStorageClient

from src.utils.constants import Constants


class DataPersistence:
    storage_provider = None
    connection_string = None
    sqlite_db_path = "sqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), Constants.sqlite_db_file_name
    )
    sqlite_db_path_async = "sqlite+aiosqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), Constants.sqlite_db_file_name
    )
    engine = None
    connection = None

    def __init__(self, enable_storage_provider: bool = False) -> None:
        self.enable_storage_provider = enable_storage_provider
        self._initiate_database()

    def _create_engine(self) -> None:
        self.engine = create_engine(self.sqlite_db_path)

    def _connect(self) -> None:
        self.connection = self.engine.connect()

    def _execute(self, query: str) -> None:
        self.connection.execute(query)

    def _close(self) -> None:
        self.connection.close()

    def _initiate_database(self) -> None:
        self._create_engine()
        self._connect()
        self._execute(
            text(
                """CREATE TABLE IF NOT EXISTS users (
                                "id" UUID PRIMARY KEY,
                                "identifier" TEXT NOT NULL UNIQUE,
                                "metadata" JSONB NOT NULL,
                                "createdAt" TEXT
                            );"""
            )
        )
        self._execute(
            text(
                """CREATE TABLE IF NOT EXISTS threads (
                                "id" UUID PRIMARY KEY,
                                "createdAt" TEXT,
                                "name" TEXT,
                                "userId" UUID,
                                "userIdentifier" TEXT,
                                "tags" TEXT[],
                                "metadata" JSONB,
                                FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
                            );"""
            )
        )
        self._execute(
            text(
                """CREATE TABLE IF NOT EXISTS steps (
                                "id" UUID PRIMARY KEY,
                                "name" TEXT NOT NULL,
                                "type" TEXT NOT NULL,
                                "threadId" UUID NOT NULL,
                                "parentId" UUID,
                                "streaming" BOOLEAN NOT NULL,
                                "waitForAnswer" BOOLEAN,
                                "isError" BOOLEAN,
                                "metadata" JSONB,
                                "tags" TEXT[],
                                "input" TEXT,
                                "output" TEXT,
                                "createdAt" TEXT,
                                "start" TEXT,
                                "end" TEXT,
                                "generation" JSONB,
                                "showInput" TEXT,
                                "language" TEXT,
                                "indent" INT,
                                FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
                            );"""
            )
        )
        self._execute(
            text(
                """CREATE TABLE IF NOT EXISTS elements (
                                "id" UUID PRIMARY KEY,
                                "threadId" UUID,
                                "type" TEXT,
                                "url" TEXT,
                                "chainlitKey" TEXT,
                                "name" TEXT NOT NULL,
                                "display" TEXT,
                                "objectKey" TEXT,
                                "size" TEXT,
                                "page" INT,
                                "language" TEXT,
                                "forId" UUID,
                                "mime" TEXT,
                                "props" JSONB,
                                FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
                        );"""
            )
        )
        self._execute(
            text(
                """CREATE TABLE IF NOT EXISTS feedbacks (
                                "id" UUID PRIMARY KEY,
                                "forId" UUID NOT NULL,
                                "threadId" UUID NOT NULL,
                                "value" INT NOT NULL,
                                "comment" TEXT,
                                FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
                            );"""
            )
        )
        self._close()

    def get_connection_url(self) -> str:
        return self.sqlite_db_path

    def get_connection_url_async(self) -> str:
        return self.sqlite_db_path_async

    def get_storage_provider(self) -> None | BaseStorageClient:
        if self.enable_storage_provider:
            raise NotImplementedError("Storage provider not implemented")
        return self.storage_provider
