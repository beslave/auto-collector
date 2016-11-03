import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()


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
