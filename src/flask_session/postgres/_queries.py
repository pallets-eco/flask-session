from psycopg2 import sql


class Queries:
    def __init__(self, schema: str, table: str) -> None:
        """Class to hold all the queries used by the session interface.

        Args:
            schema (str): The name of the schema to use for the session data.
            table (str): The name of the table to use for the session data.
        """
        self.schema = schema
        self.table = table

    @property
    def create_schema(self) -> str:
        return sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema};").format(
            schema=sql.Identifier(self.schema)
        )

    @property
    def create_table(self) -> str:
        uq_idx = sql.Identifier(f"uq_{self.table}_session_id")
        expiry_idx = sql.Identifier(f"{self.table}_expiry_idx")
        return sql.SQL(
            """CREATE TABLE IF NOT EXISTS {schema}.{table} (
            session_id VARCHAR(255) NOT NULL PRIMARY KEY,
            created TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
            data BYTEA,
            expiry TIMESTAMP WITHOUT TIME ZONE
        );

        --- Unique session_id
        CREATE UNIQUE INDEX IF NOT EXISTS
            {uq_idx} ON {schema}.{table} (session_id);

        --- Index for expiry timestamp
        CREATE INDEX IF NOT EXISTS
            {expiry_idx} ON {schema}.{table} (expiry);"""
        ).format(
            schema=sql.Identifier(self.schema),
            table=sql.Identifier(self.table),
            uq_idx=uq_idx,
            expiry_idx=expiry_idx,
        )

    @property
    def retrieve_session_data(self) -> str:
        return sql.SQL(
            """--- If the current sessions is expired, delete it
            DELETE FROM {schema}.{table}
            WHERE session_id = %(session_id)s AND expiry < NOW();
            --- Else retrieve it
            SELECT data FROM {schema}.{table} WHERE session_id = %(session_id)s;
        """
        ).format(schema=sql.Identifier(self.schema), table=sql.Identifier(self.table))

    @property
    def upsert_session(self) -> str:
        return sql.SQL(
            """INSERT INTO {schema}.{table} (session_id, data, expiry)
            VALUES (%(session_id)s, %(data)s, %(expiry)s)
            ON CONFLICT (session_id)
            DO UPDATE SET data = %(data)s, expiry = %(expiry)s;
        """
        ).format(schema=sql.Identifier(self.schema), table=sql.Identifier(self.table))

    @property
    def delete_expired_sessions(self) -> str:
        return sql.SQL("DELETE FROM {schema}.{table} WHERE expiry < NOW();").format(
            schema=sql.Identifier(self.schema), table=sql.Identifier(self.table)
        )

    @property
    def delete_session(self) -> str:
        return sql.SQL(
            "DELETE FROM {schema}.{table} WHERE session_id = %(session_id)s;"
        ).format(schema=sql.Identifier(self.schema), table=sql.Identifier(self.table))
