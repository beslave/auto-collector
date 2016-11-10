import sqlalchemy as sa

from auto.models.base import Base, WithOrigin
from auto.models.complectation.complectation import Complectation


class BaseBody:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    body_type_id = sa.Column(sa.Integer, nullable=True)
    doors = sa.Column(sa.Integer, nullable=True)
    seats = sa.Column(sa.Integer, nullable=True)


class Body(BaseBody, Base):
    __tablename__ = 'auto_body'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
        sa.ForeignKeyConstraint(['body_type_id'], ['auto_bodytype.id']),
    )


class OriginBody(BaseBody, WithOrigin(Body), Base):
    __tablename__ = 'auto_originbody'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['body_type_id', 'origin'],
            ['auto_originbodytype.id', 'auto_originbodytype.origin'],
        ),
    )
