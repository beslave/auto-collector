import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEnginePosition:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class EnginePosition(BaseEnginePosition, Base):
    __tablename__ = 'auto_engineposition'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginEnginePosition(BaseEnginePosition, WithOrigin(EnginePosition), Base):
    __tablename__ = 'auto_originengineposition'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
