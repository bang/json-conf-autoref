# Exceptions
class LimitException(Exception):
    def ___init__(self, expression, message):
        self.expression = expression
        self.message = message
        super(ValidationError, self).__init__(message)

class NoInputData(Exception):
    def ___init__(self, expression, message):
        self.expression = expression
        self.message = message
        super(ValidationError, self).__init__(message)

class InvalidParam(Exception):
    def ___init__(self, expression, message):

        self.expression = expression
        self.message = message
        super(ValidationError, self).__init__(message)

class InvalidComplexListValues(Exception):
    def ___init__(self, expression, message):

        self.expression = expression
        self.message = message
        super(ValidationError, self).__init__(message)

class PathNotDefined(Exception):
    def ___init__(self, expression, message):

        self.expression = expression
        self.message = message
        super(ValidationError, self).__init__(message)


