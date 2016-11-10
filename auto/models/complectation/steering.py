import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseSteering:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    amplifier_id = sa.Column(sa.Integer, nullable=True)
    spread_diameter = sa.Column(sa.Integer, nullable=True)  # cm


class Steering(BaseSteering, Base):
    __tablename__ = 'auto_steering'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
        sa.ForeignKeyConstraint(['amplifier_id'], ['auto_steeramplifier.id']),
    )


class OriginSteering(BaseSteering, WithOrigin(Steering), Base):
    __tablename__ = 'auto_originsteering'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['amplifier_id', 'origin'],
            ['auto_originsteeramplifier.id', 'auto_originsteeramplifier.origin'],
        ),
    )
