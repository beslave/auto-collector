import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()


class BaseBrand:
    id = sa.Column(
        sa.Integer,
        primary_key=True,
    )
    name = sa.Column(
        sa.String,
    )


class BaseModel:
    id = sa.Column(
        sa.Integer,
        primary_key=True,
    )
    name = sa.Column(sa.String)


class BaseComplectation:
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class BaseAdvertisement:
    id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column(sa.String)
    is_new = sa.Column(sa.Boolean)
    year = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
    preview = sa.Column(sa.String, nullable=True)


def WithOrigin(RealModel):
    class _WithOrigin:
        origin = sa.Column(sa.String, index=True)

        created_at = sa.Column(sa.DateTime(timezone=False))
        updated_at = sa.Column(sa.DateTime(timezone=False))

        @declared_attr
        def real_instance(cls):
            return sa.Column(
                sa.Integer,
                sa.ForeignKey(RealModel.id),
                nullable=True,
            )

    return _WithOrigin


class Brand(BaseBrand, Base):
    __tablename__ = 'auto_brand'
    __table_args__ = (
        sa.UniqueConstraint('name', name='name_uc'),
    )


class Model(BaseModel, Base):
    brand_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Brand.id),
        nullable=False,
    )

    __tablename__ = 'auto_model'
    __table_args__ = (
        sa.UniqueConstraint('name', 'brand_id', name='name_brand_uc'),
    )


class Complectation(BaseComplectation, Base):
    model_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Model.id),
        nullable=False,
    )

    __tablename__ = 'auto_complectation'
    __table_args__ = (
        sa.UniqueConstraint('name', 'model_id', name='name_model_uc'),
    )


class Advertisement(BaseAdvertisement, Base):
    __tablename__ = 'auto_advertisement'

    model_id = sa.Column(sa.Integer, sa.ForeignKey(Model.id), nullable=False)
    complectation_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Complectation.id),
        nullable=True,
    )


class OriginBrand(BaseBrand, WithOrigin(Brand), Base):
    __tablename__ = 'auto_originbrand'
    __table_args__ = (
        sa.UniqueConstraint('origin', 'name', name='origin_name_uc'),
    )


class OriginModel(BaseModel, WithOrigin(Model), Base):
    brand_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(OriginBrand.id),
        nullable=False,
    )

    __tablename__ = 'auto_originmodel'
    __table_args__ = (
        sa.UniqueConstraint(
            'origin', 'name', 'brand_id',
            name='origin_name_brand_uc'
        ),
    )


class OriginComplectation(BaseComplectation, WithOrigin(Complectation), Base):
    model_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(OriginModel.id),
        nullable=False,
    )

    __tablename__ = 'auto_origincomplectation'
    __table_args__ = (
        sa.UniqueConstraint(
            'origin', 'name', 'model_id',
            name='origin_name_model_uc'
        ),
    )


class OriginAdvertisement(BaseAdvertisement, WithOrigin(Advertisement), Base):
    __tablename__ = 'auto_originadvertisement'

    model_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(OriginModel.id),
        nullable=False,
    )
    complectation_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(OriginComplectation.id),
        nullable=True,
    )
    origin_url = sa.Column(
        sa.String,
        nullable=True,
    )
