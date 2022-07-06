class ModelClassNameMixin:
    @property
    def model_name(self):
        x = self.__class__.__name__
        return x
