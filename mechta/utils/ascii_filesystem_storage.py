import unicodedata2
import pytils
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.files.utils import validate_file_name


class ASCIIFileSystemStorage(FileSystemStorage):
    """
    Для автоматической транслитерации всех загружаемых файлов
    """
    pre_name = ''

    def get_pre_name(self, name, max_length=None):
        name = unicodedata2.normalize('NFKD', pytils.translit.translify(name)).replace(' ', '-'). \
            encode('ascii', 'ignore').decode('utf-8')
        self.pre_name = self.get_available_name(name, max_length=max_length)
        return self.pre_name


    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        if self.pre_name:
            name = self.pre_name
        if not hasattr(content, "chunks"):
            content = File(content, name)
        name = self._save(name, content)
        # Ensure that the name returned from the storage system is still valid.
        validate_file_name(name, allow_relative_path=True)
        return name