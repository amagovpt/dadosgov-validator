import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Returns True if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_upload_bytes(file_name: str, file_bytes: bytes, unique_id: str, upload_folder: str) -> str:
    """
    Saves an uploaded file to disk with a unique name to avoid collisions.

    Returns the absolute path to the saved file.
    """
    original_name = secure_filename(file_name)
    extension = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{unique_id}.{extension}"
    file_path = os.path.join(upload_folder, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return unique_id, os.path.abspath(file_path)


def remove_file(file_path: str):
    """Deletes a file from disk if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)
