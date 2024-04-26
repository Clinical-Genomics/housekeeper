from housekeeper.store.store import Store


class FileService:

    def __init__(self, store: Store):
        self.store = store
