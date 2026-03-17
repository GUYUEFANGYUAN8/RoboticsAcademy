# File Abstraction Layer

from abc import ABC, abstractmethod
import os
import shutil
from .project_view import list_dir
from .exceptions import (
    BinaryNotSupported,
    InvalidPath,
    ResourceNotExists,
    ResourceAlreadyExists,
)


class FAL(ABC):
    """File Abstraction Layer"""

    def __init__(self, academy="", helper=""):
        self.academy = academy
        self.helper = helper
        self.user = None

    def set_user(self, user):
        self.user = user

    @abstractmethod
    def academy_path(self) -> str:
        pass

    def exercise_path(self, exercise_id) -> str:
        """Return the workspace directory for a single exercise."""
        return self.path_join(self.academy_path(), exercise_id)

    def helpers_path(self, exercise_id) -> str:
        """Return the directory that stores helper templates for an exercise."""
        return self.path_join(self.helper, exercise_id)

    def exercise_helper_path(self, project_id, language) -> str:
        """Resolve the helper template directory for a project/language pair."""
        return self.path_join(self.helpers_path(project_id), f"{language}_template/")

    @abstractmethod
    def path_join(self, a: str, b: str) -> str:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def isdir(self, path: str) -> bool:
        pass

    @abstractmethod
    def isfile(self, path: str) -> bool:
        pass

    @abstractmethod
    def create(self, path: str, content):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) > 0:
            raise ResourceAlreadyExists(path)

    @abstractmethod
    def create_binary(self, path: str, content):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) > 0:
            raise ResourceAlreadyExists(path)

    @abstractmethod
    def write(self, path: str, content):
        size = self.exists(path)
        if size < 0:
            raise ResourceNotExists(path)

    @abstractmethod
    def write_binary(self, path: str, content):
        size = self.exists(path)
        if size < 0:
            raise ResourceNotExists(path)

    @abstractmethod
    def read(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

    @abstractmethod
    def read_binary(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

    @abstractmethod
    def listdirs(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

        if not self.isdir(path):
            raise ResourceNotExists(path)

    @abstractmethod
    def listfiles(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

        if not self.isdir(path):
            raise ResourceNotExists(path)

    @abstractmethod
    def list_formatted(self, path: str, base_group: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

        if not self.isdir(path):
            raise ResourceNotExists(path)

    @abstractmethod
    def mkdir(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) >= 0:
            raise ResourceAlreadyExists(path)

    @abstractmethod
    def renamefile(self, old_path: str, new_path: str):
        if ".." in new_path:
            raise InvalidPath(new_path)

        if self.exists(old_path) < 0:
            raise ResourceNotExists(old_path)

        if self.exists(new_path) >= 0:
            raise ResourceAlreadyExists(new_path)

    @abstractmethod
    def renamedir(self, old_path: str, new_path: str):
        if ".." in new_path:
            raise InvalidPath(new_path)

        if self.exists(old_path) < 0:
            raise ResourceNotExists(old_path)

        if self.exists(new_path) >= 0:
            raise ResourceAlreadyExists(new_path)

    @abstractmethod
    def removefile(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        size = self.exists(path)
        if size < 0:
            raise ResourceNotExists(path)

        if not self.isfile(path):
            raise ResourceNotExists(path)

    @abstractmethod
    def removedir(self, path: str):
        if ".." in path:
            raise InvalidPath(path)

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

        if not self.isdir(path):
            raise ResourceNotExists(path)

    @abstractmethod
    def dir_size(self, path):
        if ".." in path:
            raise InvalidPath(path)

        path = self.path_join(path, "")

        if self.exists(path) < 0:
            raise ResourceNotExists(path)

        if not self.isdir(path):
            raise ResourceNotExists(path)

    def filename(self, path: str) -> str:
        """Extract the filename without extension from a full path."""
        return os.path.splitext(os.path.basename(path))[0]


class FAL_RA(FAL):
    """File Abstraction Layer"""

    def __init__(self, base, helper):
        FAL.__init__(self, base, helper)

    def academy_path(self) -> str:
        """Return the base directory that contains user exercise files."""
        return self.path_join(self.academy, "filesystem")

    def path_join(self, a: str, b: str) -> str:
        return os.path.join(a, b)

    def exists(self, path: str) -> bool:
        """Return -1 for missing paths, 0 for directories, or file size for files."""
        if not os.path.exists(path):
            return -1

        if os.path.isdir(path):  # It is a dir
            return 0

        return os.path.getsize(path)

    def isdir(self, path: str) -> bool:
        return os.path.isdir(path)

    def isfile(self, path: str) -> bool:
        return os.path.isfile(path)

    def create(self, path: str, content):
        """Create a text file and make it writable from the containerized stack."""
        super().create(path, content)

        with open(path, "w") as f:
            f.write(content)
        os.chmod(path, 0o777)

    def create_binary(self, path: str, content):
        """Create a binary file and apply the same permissive file mode."""
        super().create_binary(path, content)

        with open(path, "wb") as f:
            f.write(content)
        os.chmod(path, 0o777)

    def write(self, path: str, content):
        """Overwrite a text file and keep the expected writable permissions."""
        super().write(path, content)

        with open(path, "w") as f:
            f.write(content)
        os.chmod(path, 0o777)

    def write_binary(self, path: str, content):
        """Overwrite a binary file and keep the expected writable permissions."""
        super().write_binary(path, content)

        with open(path, "wb") as f:
            f.write(content)
        os.chmod(path, 0o777)

    def read(self, path: str) -> str:
        """Read a text file and surface binary payloads as API-level errors."""
        super().read(path)

        try:
            with open(path, "r") as f:
                return f.read()
        except Exception:
            raise BinaryNotSupported(path)

    def read_binary(self, path: str) -> str:
        """Read raw bytes from a file once the path has been validated."""
        super().read(path)

        with open(path, "rb") as f:
            return f.read()

    def listdirs(self, path: str):
        """Return the direct child directories for a validated path."""
        super().listdirs(path)

        return [d for d in os.listdir(path) if self.isdir(self.path_join(path, d))]

    def listfiles(self, path: str):
        """Return the direct child files for a validated path."""
        super().listfiles(path)

        return [d for d in os.listdir(path) if self.isfile(self.path_join(path, d))]

    def list_formatted(self, path: str, base_group: str):
        """Build the explorer tree structure consumed by the frontend."""
        super().list_formatted(path, base_group)

        return list_dir(path, path, base_group=base_group)

    def mkdir(self, path: str):
        """Create a directory tree and expose it with writable permissions."""
        super().mkdir(path)

        os.makedirs(path)
        os.chmod(path, mode=0o777)

    def renamefile(self, old_path: str, new_path: str):
        """Rename a file after the shared validation checks have run."""
        super().renamefile(old_path, new_path)

        os.rename(old_path, new_path)

    def renamedir(self, old_path: str, new_path: str):
        """Rename a directory after the shared validation checks have run."""
        super().renamedir(old_path, new_path)

        os.rename(old_path, new_path)

    def removefile(self, path: str):
        """Delete a validated file path."""
        super().removefile(path)

        os.remove(path)

    def removedir(self, path: str):
        """Delete a validated directory tree."""
        super().removedir(path)

        shutil.rmtree(path)

    def dir_size(self, path):
        """Calculate directory size while ignoring symbolic links."""
        super().dir_size(path)

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size
