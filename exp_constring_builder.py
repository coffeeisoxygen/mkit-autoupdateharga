"""experimenting accepting connection string management with a builder pattern.


used for otomax (sqlsever) and aioodbc (odbc).
will be stored as a encrypted string
the key is machine id with some salt
so it can only be decrypted on the same machine
"""

import pyodbc
from loguru import logger


class ConStringBuilder:
    def __init__(self, auto_detect_driver: bool = True):
        self.driver = None
        self.server = None
        self.database = None
        self.uid = None
        self.pwd = None
        self.trusted_connection = None
        self.mars = None  # Multiple Active Result Sets
        self.encrypt = None  # Connection encryption
        if auto_detect_driver:
            try:
                self.driver = self.auto_detect_driver()
            except Exception as e:
                logger.warning(f"Auto detect driver failed: {e}")

    @staticmethod
    def auto_detect_driver():
        # Cari driver SQL Server ODBC terbaru secara otomatis
        drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
        logger.debug(f"Available SQL Server ODBC drivers: {drivers}")
        if not drivers:
            logger.warning("No suitable SQL Server ODBC driver found on this system.")
            raise RuntimeError(
                "No suitable SQL Server ODBC driver found on this system."
            )

        # Urutkan driver berdasarkan versi (jika ada angka di nama driver)
        def extract_version(name):
            import re

            match = re.search(r"ODBC Driver (\d+)", name)
            return int(match.group(1)) if match else 0

        drivers_sorted = sorted(drivers, key=extract_version, reverse=True)
        selected = drivers_sorted[0]
        logger.debug(f"Auto-detected ODBC driver: {selected}")
        return selected

    def set_driver(self, driver: str):
        self.driver = driver
        return self

    def set_server(self, server: str):
        self.server = server
        return self

    def set_database(self, database: str):
        self.database = database
        return self

    def set_uid(self, uid: str):
        self.uid = uid
        return self

    def set_pwd(self, pwd: str):
        self.pwd = pwd
        return self

    def set_trusted_connection(self, trusted_connection: bool):
        self.trusted_connection = trusted_connection
        return self

    def set_mars(self, enable: bool):
        self.mars = enable
        return self

    def set_encrypt(self, encrypt: bool):
        self.encrypt = encrypt
        return self

    def build(self) -> str:
        # Require driver to be set explicitly
        if not self.driver:
            raise ValueError(
                "ODBC driver must be set explicitly. Use set_driver() or auto_detect_driver()."
            )
        parts = []
        if self.driver:
            parts.append(f"DRIVER={{{self.driver}}}")
        if self.server:
            parts.append(f"SERVER={self.server}")
        if self.database:
            parts.append(f"DATABASE={self.database}")
        # Windows Auth: Trusted_Connection=yes, SQL Auth: UID/PWD
        if self.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            # SQL Server Auth mode
            if not self.uid or not self.pwd:
                raise ValueError(
                    "UID and PWD must be set for SQL Server Authentication (Trusted_Connection=no)"
                )
            parts.append(f"UID={self.uid}")
            parts.append(f"PWD={self.pwd}")
            parts.append("Trusted_Connection=no")
        if self.mars is not None:
            parts.append(f"MARS_Connection={'Yes' if self.mars else 'No'}")
        if self.encrypt is not None:
            parts.append(f"Encrypt={'Yes' if self.encrypt else 'No'}")
        return ";".join(parts)

    def get_sqlalchemy_url(self) -> str:
        """Return SQLAlchemy connection URL using pyodbc driver."""
        import urllib.parse

        con_str = self.build()
        return f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(con_str)}"

    def get_aiodbc_dsn(self) -> str:
        """Return DSN string for aiodbc."""
        return self.build()


# test call
def main():
    builder_sql = ConStringBuilder(auto_detect_driver=True)
    con_str_sql = (
        builder_sql.set_server("localhost")
        .set_database("mydb")
        .set_uid("myuser")
        .set_pwd("mypassword")
        .set_trusted_connection(False)
        .set_mars(True)
        .set_encrypt(True)
        .build()
    )
    print("SQL Server Auth:", con_str_sql)

    builder_win = ConStringBuilder(auto_detect_driver=True)
    con_str_win = (
        builder_win.set_server("localhost")
        .set_database("mydb")
        .set_trusted_connection(True)
        .set_mars(True)
        .set_encrypt(True)
        .build()
    )
    print("Windows Auth:", con_str_win)


if __name__ == "__main__":
    main()
