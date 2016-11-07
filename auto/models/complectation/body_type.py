import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseBodyType:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class BodyType(BaseBodyType, Base):
    __tablename__ = 'auto_bodytype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginBodyType(BaseBodyType, WithOrigin(BodyType), Base):
    __tablename__ = 'auto_originbodytype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
