import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseSteerAmplifier:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class SteerAmplifier(BaseSteerAmplifier, Base):
    __tablename__ = 'auto_steeramplifier'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginSteerAmplifier(BaseSteerAmplifier, WithOrigin(SteerAmplifier), Base):
    __tablename__ = 'auto_originsteeramplifier'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
