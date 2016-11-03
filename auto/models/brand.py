import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseBrand:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(timezone=False))
    updated_at = sa.Column(sa.DateTime(timezone=False))


class Brand(BaseBrand, Base):
    __tablename__ = 'auto_brand'
    __table_args__ = (
        sa.UniqueConstraint('name', name='name_uc'),
        sa.PrimaryKeyConstraint('id'),
    )


class OriginBrand(BaseBrand, WithOrigin(Brand), Base):
    __tablename__ = 'auto_originbrand'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('origin', 'name'),
    )
