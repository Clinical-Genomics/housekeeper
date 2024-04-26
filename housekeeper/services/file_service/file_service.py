from housekeeper.store.models import File
from housekeeper.store.store import Store


class FileService:

    def __init__(self, store: Store):
        self.store = store

    def get_local_files(self, bundle: str, tags: list[str], version_id: int) -> list[File]:
        return self.store.get_files(
            bundle_name=bundle, tag_names=tags, version_id=version_id, is_local=True
        )

    def get_remote_files(self, bundle: str, tags: list[str], version_id: int) -> list[File]:
        return self.store.get_files(
            bundle_name=bundle, tag_names=tags, version_id=version_id, is_remote=True
        )
