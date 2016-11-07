import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseDimensions:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    length = sa.Column(sa.Integer, nullable=True)
    width = sa.Column(sa.Integer, nullable=True)
    height = sa.Column(sa.Integer, nullable=True)
    clearance = sa.Column(sa.Integer, nullable=True)
    curb_weight = sa.Column(sa.Integer, nullable=True)
    max_allowed_weight = sa.Column(sa.Integer, nullable=True)
    trunk_volume = sa.Column(sa.Integer, nullable=True)
    fuel_tank_volume = sa.Column(sa.Integer, nullable=True)
    wheel_base = sa.Column(sa.Integer, nullable=True)
    bearing_capacity = sa.Column(sa.Integer, nullable=True)


class Dimensions(BaseDimensions, Base):
    __tablename__ = 'auto_dimensions'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
    )


class OriginDimensions(BaseDimensions, WithOrigin(Dimensions), Base):
    __tablename__ = 'auto_origindimensions'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
    )
