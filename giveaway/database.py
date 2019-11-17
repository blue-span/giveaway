import contextvars
import threading
import os

import apsw
import xdg


def database_path():
    dir_path = xdg.XDG_DATA_HOME
    os.makedirs(dir_path / "giveaway", exist_ok=True)
    path = dir_path / "giveaway" / "giveaway.sqlite3"
    size = path.stat().st_size if path.exists() else -1
    print(f"database {path=!s} {size=}")
    return path


#connection = contextvars.ContextVar("connection")
connection = apsw.Connection(str(database_path()))


def connection_context():
    ctx = contextvars.copy_context()
    ctx.run(lambda: connection.set(apsw.Connection(database_dir())))
    return ctx
