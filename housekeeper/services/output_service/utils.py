from housekeeper.store.api import schema
from housekeeper.store.models import File


def format_files(files: list[File]):
    template = schema.FileSchema()
    formatted_files = []
    for file in files:
        formatted_file = template.dump(file)
        formatted_files.append(formatted_file)
    return formatted_files
