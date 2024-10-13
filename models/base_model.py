from . import db

class BaseModel:
    @classmethod
    def add(cls, **kwargs):
        try:
            new_record = cls(**kwargs)
            db.session.add(new_record)
            db.session.commit()
            return new_record
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find(cls, **kwargs):
        try:
            return cls.query.filter_by(**kwargs).all()
        except Exception as e:
            raise e
