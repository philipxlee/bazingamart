from functools import wraps
from flask import current_app


def handle_db_exceptions(func):
    """
    A decorator to handle database exceptions, logging, and transactions.
    Commits the transaction if no exceptions occur, otherwise rolls back.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            current_app.db.commit()
            return result
        except Exception as e:
            current_app.logger.error(f"Database operation failed in {func.__name__}: {str(e)}")
            current_app.db.rollback()
            return "failure"
    return wrapper