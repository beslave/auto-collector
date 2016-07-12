import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class AutoAdvertisement(Base):
    __tablename__ = 'auto_advertisement'

    id = sa.Column(sa.Integer, primary_key=True)
    brand = sa.Column(sa.String)
    model = sa.Column(sa.String)
    complectation = sa.Column(sa.String)

    is_new = sa.Column(sa.Boolean)
    year = sa.Column(sa.Integer)
