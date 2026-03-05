class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register(self, version, model):
        self.models[version] = model

    def get(self, version):
        return self.models.get(version)

    def list_versions(self):
        return list(self.models.keys())
