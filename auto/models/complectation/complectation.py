import sqlalchemy as sa

from auto.models.base import Base, WithOrigin
from auto.models.model import Model


class BaseComplectation:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class Complectation(BaseComplectation, Base):
    model_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Model.id),
        nullable=False,
    )

    __tablename__ = 'auto_complectation'
    __table_args__ = (
        sa.UniqueConstraint('name', 'model_id', name='name_model_uc'),
        sa.PrimaryKeyConstraint('id'),
    )


class OriginComplectation(BaseComplectation, WithOrigin(Complectation), Base):
    model_id = sa.Column(sa.Integer, nullable=False)

    __tablename__ = 'auto_origincomplectation'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint(
            'origin', 'name', 'model_id',
            name='origin_name_model_uc'
        ),
        sa.ForeignKeyConstraint(
            ['model_id', 'origin'],
            ['auto_originmodel.id', 'auto_originmodel.origin'],
            onupdate='CASCADE', ondelete='CASCADE',
        ),
    )
