from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper')
    
    # Add serialization rules
    serialize_only = ('id', 'name', 'difficulty')
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity')

    # Add serialization rules
    serialize_rules = ('-signups.camper', '-created_at', '-updated_at')

    # Add validation
    @validates('name')
    def validate_name(self, _, value): 
        if not value:
            raise ValueError('Camper must have a name')
        return value 
    
    @validates('age')
    def validate_age(self, _, value):
        if not 8 <= value <= 18:
            raise ValueError('Camper age must be between 8 and 18')
        return value 
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationships
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')
    
    # Add serialization rules
    serialize_rules = ('-camper.signups', '-activity.signups', 
                        '-created_at', '-updated_at')
    
    # Add validation
    @validates('time')
    def validates_time(self, _, value):
        if not 0 <= value <= 23:
            raise ValueError('Time must be between 0 and 23')
        return value
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
