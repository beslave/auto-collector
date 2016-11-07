import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEngineCylindersPosition:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class EngineCylindersPosition(BaseEngineCylindersPosition, Base):
    __tablename__ = 'auto_enginecylindersposition'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginEngineCylindersPosition(BaseEngineCylindersPosition, WithOrigin(EngineCylindersPosition), Base):
    __tablename__ = 'auto_originenginecylindersposition'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
