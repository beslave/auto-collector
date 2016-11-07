import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseTransmission:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    gearbox_type_id = sa.Column(sa.Integer, nullable=True)
    gears_count = sa.Column(sa.Integer, nullable=True)
    drive_type_id = sa.Column(sa.Integer, nullable=True)


class Transmission(BaseTransmission, Base):
    __tablename__ = 'auto_transmission'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
        sa.ForeignKeyConstraint(['gearbox_type_id'], ['auto_gearboxtype.id']),
        sa.ForeignKeyConstraint(['drive_type_id'], ['auto_drivetype.id']),
    )


class OriginTransmission(BaseTransmission, WithOrigin(Transmission), Base):
    __tablename__ = 'auto_origintransmission'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['gearbox_type_id', 'origin'],
            ['auto_origingearboxtype.id', 'auto_origingearboxtype.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['drive_type_id', 'origin'],
            ['auto_origindrivetype.id', 'auto_origindrivetype.origin'],
        ),
    )
