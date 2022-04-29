from django.db import models


class CharableListField(models.CharField):

    description = "Easy way to deal with Python lists and tuples in native style"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 5096
        kwargs["default"] = "[]"
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["default"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return []
        return eval(value)
    
    def get_prep_value(self, value):
        return str(value)