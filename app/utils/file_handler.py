import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Returns True if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_upload(file: FileStorage, upload_folder: str) -> str:
    """
    Saves an uploaded file to disk with a unique name to avoid collisions.

    Returns the absolute path to the saved file.
    """
    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    unique_id = 'dataframe_' + str(uuid.uuid4().hex)
    unique_name = f"{unique_id}.{extension}"
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return unique_id, os.path.abspath(file_path)


def remove_file(file_path: str):
    """Deletes a file from disk if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)
