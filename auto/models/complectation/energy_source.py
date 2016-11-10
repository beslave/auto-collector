import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEnergySource:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class EnergySource(BaseEnergySource, Base):
    __tablename__ = 'auto_energysource'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginEnergySource(BaseEnergySource, WithOrigin(EnergySource), Base):
    __tablename__ = 'auto_originenergysource'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
