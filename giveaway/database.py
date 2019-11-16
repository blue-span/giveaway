import contextvars
import threading

import apsw


#connection = contextvars.ContextVar("connection")
connection = apsw.Connection("giveaway.sqlite3")


def connection_context():
    ctx = contextvars.copy_context()
    ctx.run(lambda: connection.set(apsw.Connection("giveaway.sqlite3")))
    return ctx
