from bson import ObjectId
from datetime import datetime
from db import db


class Image:
    def __init__(self, uploaded_by, filename, file_content, img_id=None, date_created=None,  _id=None):
        self._id = _id
        self.img_id = img_id or str(ObjectId())
        self.uploaded_by = uploaded_by
        self.filename = filename
        self.file_content = file_content
        self.date_created = date_created or datetime.utcnow()

    def save(self):
        """ saving/updating image. """
        data_img = {
            "img_id": self.img_id,
            "uploaded_by": self.uploaded_by,
            "filename": self.filename,
            "file_content": self.file_content,
            "date_created": self.date_created,
        }
        if self._id:
            db.images.replace_one({"_id": self._id}, data_img)
        else:
            result = db.images.insert_one(data_img)
            self._id = result.inserted_id

    @classmethod
    def find_by_user(cls, user_id):
        images = db.images.find({"uploaded_by": user_id}).sort("date_created", -1)
        return [cls(**image) for image in images]
    
    @classmethod
    def creating_by_objectid(cls, uploaded_by, filename, file_content):
        return cls(uploaded_by=uploaded_by, filename=filename, file_content=file_content)