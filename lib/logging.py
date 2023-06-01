import logging


class Loggable:
    def __init__(self, class_name):
        self.logger = logging.getLogger(class_name)

    def __call__(self, *args):
        def wrapper(*_args, **_kwargs):
            self.logger.info(f".{args[0].__name__}({_args, *_kwargs.items()})")
            return args[0](*_args, **_kwargs)
        return wrapper


# @Loggable("main")
# def print_h(s):
#     print(f"Hello {s}!")


class BasicErrorHandler(Loggable):
    def __init__(self, package_name: str, expectedErrClass: type, rethrow: bool = False):
        super().__init__(package_name)
        self.expectedErrClass = expectedErrClass
        self.rethrow = rethrow

    def __call__(self, *args):
        func = super().__call__(*args)

        def wrapper(*_args):
            print(_args)
            try:
                return func(*_args)
            except self.expectedErrClass as e:
                self.logger.error(str(e))
                if self.rethrow: raise e
        return wrapper


# @BasicErrorHandler(package_name="main", expectedErrClass=KeyError, rethrow=False)
# def say_hi(mode: int = -1):
#     if (mode == 0): raise BaseException()
#     elif (mode == 1): raise KeyError()
#     else: print("hi")
