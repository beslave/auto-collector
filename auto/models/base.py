import sqlalchemy as sa

from sqlalchemy.ext.declarative import declared_attr

from migrations.models_base import Base


def WithOrigin(RealModel):
    class _WithOrigin:
        origin = sa.Column(sa.String, index=True)

        @declared_attr
        def real_instance(cls):
            return sa.Column(
                sa.Integer,
                sa.ForeignKey(RealModel.id),
                nullable=True,
            )

    return _WithOrigin
