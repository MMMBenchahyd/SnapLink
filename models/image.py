import uuid
from datetime import datetime

class Image:
    def __init__(self, uploaded_by, filename, file_content, img_id=None, date_created=None,  _id=None):
        self._id = _id
        self.img_id = img_id or str(uuid())
        self.uploaded_by = uploaded_by
        self.filename = filename
        self.file_content = file_content
        self.date_created = date_created or datetime.utcnow()
