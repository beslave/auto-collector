import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class AutoBrand(Base):
    __tablename__ = 'auto_brand'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True)


class AutoModel(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    brand_id = sa.Column(sa.Integer, sa.ForeignKey(AutoBrand.id), nullable=False)

    __tablename__ = 'auto_model'
    __table_args__ = (
        sa.UniqueConstraint('name', 'brand_id', name='name_brand_uc'),
    )


class AutoComplectation(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    model_id = sa.Column(sa.Integer, sa.ForeignKey(AutoModel.id), nullable=False)

    __tablename__ = 'auto_complectation'
    __table_args__ = (
        sa.UniqueConstraint('name', 'model_id', name='name_model_uc'),
    )


class AutoAdvertisement(Base):
    __tablename__ = 'auto_advertisement'

    id = sa.Column(sa.Integer, primary_key=True)
    model_id = sa.ForeignKey(AutoModel.id)
    complectation_id = sa.ForeignKey(AutoComplectation.id)

    is_new = sa.Column(sa.Boolean)
    year = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
