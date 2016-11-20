import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEnginePower:
    id = sa.Column(sa.Integer, autoincrement=True)
    horses = sa.Column(sa.Integer, nullable=True)
    rotations_start = sa.Column(sa.Integer, nullable=True)
    rotations_end = sa.Column(sa.Integer, nullable=True)
    max_torque = sa.Column(sa.Integer, nullable=True)
    max_torque_rotations_start = sa.Column(sa.Integer, nullable=True)
    max_torque_rotations_end = sa.Column(sa.Integer, nullable=True)


class EnginePower(BaseEnginePower, Base):
    __tablename__ = 'auto_enginepower'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['id'], ['auto_engine.id']),
    )


class OriginEnginePower(BaseEnginePower, WithOrigin(EnginePower), Base):
    __tablename__ = 'auto_originenginepower'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['id', 'origin'],
            ['auto_originengine.id', 'auto_originengine.origin'],
        ),
    )
