import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseBrand:
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class BaseModel:
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class BaseComplectation:
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class BaseAdvertisement:
    id = sa.Column(sa.Integer, primary_key=True)

    is_new = sa.Column(sa.Boolean)
    year = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)


class WithOriginMixin:
    origin = sa.Column(sa.String, index=True)


class Brand(BaseBrand, Base):
    __tablename__ = 'auto_brand'
    __table_args__ = (
        sa.UniqueConstraint('name', name='name_uc'),
    )


class Model(BaseModel, Base):
    brand_id = sa.Column(sa.Integer, sa.ForeignKey(Brand.id), nullable=False)

    __tablename__ = 'auto_model'
    __table_args__ = (
        sa.UniqueConstraint('name', 'brand_id', name='name_brand_uc'),
    )


class Complectation(BaseComplectation, Base):
    model_id = sa.Column(sa.Integer, sa.ForeignKey(Model.id), nullable=False)

    __tablename__ = 'auto_complectation'
    __table_args__ = (
        sa.UniqueConstraint('name', 'model_id', name='name_model_uc'),
    )


class Advertisement(BaseAdvertisement, Base):
    __tablename__ = 'auto_advertisement'

    model_id = sa.ForeignKey(Model.id)
    complectation_id = sa.ForeignKey(Complectation.id)


class OriginBrand(BaseBrand, WithOriginMixin, Base):
    __tablename__ = 'auto_originbrand'
    __table_args__ = (
        sa.UniqueConstraint('origin', 'name', name='origin_name_uc'),
    )


class OriginModel(BaseModel, WithOriginMixin, Base):
    brand_id = sa.Column(sa.Integer, sa.ForeignKey(OriginBrand.id), nullable=False)

    __tablename__ = 'auto_originmodel'
    __table_args__ = (
        sa.UniqueConstraint('origin', 'name', 'brand_id', name='origin_name_brand_uc'),
    )


class OriginComplectation(BaseComplectation, WithOriginMixin, Base):
    model_id = sa.Column(sa.Integer, sa.ForeignKey(OriginModel.id), nullable=False)

    __tablename__ = 'auto_origincomplectation'
    __table_args__ = (
        sa.UniqueConstraint('origin', 'name', 'model_id', name='origin_name_model_uc'),
    )


class OriginAdvertisement(BaseAdvertisement, WithOriginMixin, Base):
    __tablename__ = 'auto_originadvertisement'

    model_id = sa.ForeignKey(Model.id)
    complectation_id = sa.ForeignKey(OriginComplectation.id)