import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseState:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String)


class State(BaseState, Base):
    __tablename__ = 'auto_state'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginState(BaseState, WithOrigin(State), Base):
    __tablename__ = 'auto_originstate'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('origin', 'name'),
    )
