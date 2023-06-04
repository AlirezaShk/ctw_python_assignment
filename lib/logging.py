from typing import Optional
import logging
from flask_restx.errors import abort
from werkzeug.exceptions import HTTPException


class Loggable:
    """Logging decorator. Logs the input and output of functions.

    Example:
        @Loggable("main")
        def print_h(s):
            print(f"Hello {s}!")
    """
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


class BasicErrorHandler(Loggable):
    """Logging and error handling decorator.

    Does 3 functionalities:
        1. Logs the input and output of functions (like Loggable).
        2. Catches only the `expectedErrClass` errors.
        3. Rethrows the errors as the `rethrow_as` type.

    Example:
        @BasicErrorHandler(package_name="main", expectedErrClass=KeyError, rethrow=ValidationError)
        def say_hi(mode: int = -1):
            if (mode == 0): raise BaseException()
            elif (mode == 1): raise KeyError()
            else: print("hi")
    """
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


class APIErrorHandler(Loggable):
    """Logging and error handling decorator, suited for API results.

    Functions more or less like `BasicErrorHandler`. The improvements are that:
        1. Aborts the application if the `expectedErrClass` is caught with the provied `code` and `message`.
            It also decorates the `HTTPException` that is raised by the `flask_restx.errors.abort` method;
            it formats the returning message to the client-side according to the standards provided by
            the project. (Turns client response format to {"info": {"error": <message>}})
        2. If the caught error is a `HTTPException`, it won't decorate the message of it further.

    """
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
