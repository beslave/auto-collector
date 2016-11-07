import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseGearboxType:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class GearboxType(BaseGearboxType, Base):
    __tablename__ = 'auto_gearboxtype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginGearboxType(BaseGearboxType, WithOrigin(GearboxType), Base):
    __tablename__ = 'auto_origingearboxtype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
