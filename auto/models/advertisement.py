import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseAdvertisement:
    id = sa.Column(sa.Integer, autoincrement=True)
    created_at = sa.Column(sa.DateTime(timezone=False))
    updated_at = sa.Column(sa.DateTime(timezone=False))

    model_id = sa.Column(sa.Integer, nullable=False)
    complectation_id = sa.Column(sa.Integer, nullable=True)

    name = sa.Column(sa.String)
    is_new = sa.Column(sa.Boolean)
    year = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
    preview = sa.Column(sa.String, nullable=True)
    origin_url = sa.Column(sa.String, nullable=True)


class Advertisement(BaseAdvertisement, Base):
    __tablename__ = 'auto_advertisement'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
        sa.ForeignKeyConstraint(['model_id'], ['auto_model.id']),
    )


class OriginAdvertisement(BaseAdvertisement, WithOrigin(Advertisement), Base):
    __tablename__ = 'auto_originadvertisement'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['model_id', 'origin'],
            ['auto_originmodel.id', 'auto_originmodel.origin'],
            onupdate='CASCADE', ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
            onupdate='CASCADE', ondelete='SET NULL',
        ),
    )
