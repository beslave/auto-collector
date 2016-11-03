import sqlalchemy as sa

from auto.models.base import Base, WithOrigin
from auto.models.brand import Brand


class BaseModel:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(timezone=False))
    updated_at = sa.Column(sa.DateTime(timezone=False))


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
