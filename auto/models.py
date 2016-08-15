import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()


class BaseBrand:
    id = sa.Column(sa.Integer)
    name = sa.Column(
        sa.String,
    )


class BaseModel:
    id = sa.Column(sa.Integer)
    name = sa.Column(sa.String)


class BaseComplectation:
    id = sa.Column(sa.Integer)
    name = sa.Column(sa.String)


class BaseAdvertisement:
    id = sa.Column(sa.Integer)

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
        sa.PrimaryKeyConstraint('id'),
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
        sa.PrimaryKeyConstraint('id'),
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
        sa.PrimaryKeyConstraint('id'),
    )


class Advertisement(BaseAdvertisement, Base):
    __tablename__ = 'auto_advertisement'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
    )

    model_id = sa.Column(sa.Integer, sa.ForeignKey(Model.id), nullable=False)
    complectation_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Complectation.id),
        nullable=True,
    )


class OriginBrand(BaseBrand, WithOrigin(Brand), Base):
    __tablename__ = 'auto_originbrand'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('origin', 'name'),
    )


class OriginModel(BaseModel, WithOrigin(Model), Base):
    brand_id = sa.Column(sa.Integer, nullable=False)

    __tablename__ = 'auto_originmodel'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint(
            'origin', 'name', 'brand_id',
            name='origin_name_brand_uc'
        ),
        sa.ForeignKeyConstraint(
            ['brand_id', 'origin'],
            ['auto_originbrand.id', 'auto_originbrand.origin'],
            onupdate='CASCADE', ondelete='CASCADE',
        ),
    )


class OriginComplectation(BaseComplectation, WithOrigin(Complectation), Base):
    model_id = sa.Column(sa.Integer, nullable=False)

    __tablename__ = 'auto_origincomplectation'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint(
            'origin', 'name', 'model_id',
            name='origin_name_model_uc'
        ),
        sa.ForeignKeyConstraint(
            ['model_id', 'origin'],
            ['auto_originmodel.id', 'auto_originmodel.origin'],
            onupdate='CASCADE', ondelete='CASCADE',
        ),
    )


class OriginAdvertisement(BaseAdvertisement, WithOrigin(Advertisement), Base):
    __tablename__ = 'auto_originadvertisement'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['model_id', 'origin'],
            ['auto_originmodel.id', 'auto_originmodel.origin'],
            onupdate='CASCADE', ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
            onupdate='CASCADE', ondelete='SET NULL',
        ),
    )

    model_id = sa.Column(sa.Integer, nullable=False)
    complectation_id = sa.Column(sa.Integer, nullable=True)
    origin_url = sa.Column(sa.String, nullable=True)
