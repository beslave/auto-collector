import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEngineFuelRate:
    id = sa.Column(sa.Integer, autoincrement=True)
    mixed = sa.Column(sa.Integer, nullable=False)
    urban = sa.Column(sa.Integer, nullable=True)
    extra_urban = sa.Column(sa.Integer, nullable=True)


class EngineFuelRate(BaseEngineFuelRate, Base):
    __tablename__ = 'auto_enginefuelrate'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['id'], ['auto_engine.id']),
    )


class OriginEngineFuelRate(BaseEngineFuelRate, WithOrigin(EngineFuelRate), Base):
    __tablename__ = 'auto_originenginefuelrate'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['id', 'origin'],
            ['auto_originengine.id', 'auto_originengine.origin'],
        ),
    )
