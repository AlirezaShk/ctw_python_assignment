from typing import Optional
import logging
from flask_restx.errors import abort
from werkzeug.exceptions import HTTPException


class Loggable:
    def __init__(self, class_name):
        self.logger = logging.getLogger(class_name)

    def __call__(self, *args):
        def wrapper(*_args, **_kwargs):
            try:
                val = args[0](*_args, **_kwargs)
                self.logger.info(f".{args[0].__name__}({_args, *_kwargs.items()}) => {val}")
                return val
            except BaseException as e:
                self.logger.info(f".{args[0].__name__}({_args, *_kwargs.items()})")
                raise e
        return wrapper


# @Loggable("main")
# def print_h(s):
#     print(f"Hello {s}!")


class BasicErrorHandler(Loggable):
    def __init__(self, package_name: str, expectedErrClass: type, rethrow_as: Optional[type] = None):
        super().__init__(package_name)
        self.expectedErrClass = expectedErrClass
        self.rethrow_as = rethrow_as

    def __call__(self, *args):
        func = super().__call__(*args)

        def wrapper(*_args):
            try:
                return func(*_args)
            except self.expectedErrClass as e:
                self.logger.error(str(e))
                if self.rethrow_as:
                    if self.rethrow_as == self.expectedErrClass:
                        raise e
                    else:
                        raise self.rethrow_as
        return wrapper


# @BasicErrorHandler(package_name="main", expectedErrClass=KeyError, rethrow=False)
# def say_hi(mode: int = -1):
#     if (mode == 0): raise BaseException()
#     elif (mode == 1): raise KeyError()
#     else: print("hi")

class APIErrorHandler(Loggable):
    def __init__(self, package_name: str, expectedErrClass: type, code: int, message: Optional[str] = None):
        super().__init__(package_name)
        self.expectedErrClass = expectedErrClass
        self.code = code
        self.message = message

    def __call__(self, *args):
        func = super().__call__(*args)

        def wrapper(*_args):
            try:
                return func(*_args)
            except self.expectedErrClass as e1:
                # If it's an HTTPException, then don't redecorate it
                if isinstance(e1, HTTPException):
                    # If HTTPException has a message with it, raise it
                    #  (If it doesn't have a description, continue to add description to it)
                    if e1.description:
                        raise e1
                # Otherwise, log it and abort the application
                self.logger.error(str(e1))
                try:
                    abort(self.code, self.message or str(e1))
                except HTTPException as e2:
                    # These statements will always be executed; they act as error message decorator
                    e2.data = {"info": {"error": e2.data["message"]}}
                    raise e2
        return wrapper
