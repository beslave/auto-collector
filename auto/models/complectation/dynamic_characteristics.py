import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseDynamicCharacteristics:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    max_velocity = sa.Column(sa.Integer, nullable=True)
    acceleration_time_to_100 = sa.Column(sa.Integer, nullable=True)


class DynamicCharacteristics(BaseDynamicCharacteristics, Base):
    __tablename__ = 'auto_dynamiccharacteristics'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
    )


class OriginDynamicCharacteristics(BaseDynamicCharacteristics, WithOrigin(DynamicCharacteristics), Base):
    __tablename__ = 'auto_origindynamiccharacteristics'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
    )
