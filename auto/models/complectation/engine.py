import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseEngine:
    id = sa.Column(sa.Integer, autoincrement=True)
    complectation_id = sa.Column(sa.Integer, nullable=False)
    position_id = sa.Column(sa.Integer, nullable=True)
    energy_source_id = sa.Column(sa.Integer, nullable=True)
    volume = sa.Column(sa.Integer, nullable=True)
    cylinders = sa.Column(sa.Integer, nullable=True)
    cylinders_position_id = sa.Column(sa.Integer, nullable=True)
    valves_count = sa.Column(sa.Integer, nullable=True)
    co2_emission = sa.Column(sa.Integer, nullable=True)
    euro_toxicity_norms = sa.Column(sa.Integer, nullable=True)


class Engine(BaseEngine, Base):
    __tablename__ = 'auto_engine'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['complectation_id'], ['auto_complectation.id']),
        sa.ForeignKeyConstraint(['position_id'], ['auto_engineposition.id']),
        sa.ForeignKeyConstraint(['energy_source_id'], ['auto_energysource.id']),
        sa.ForeignKeyConstraint(['cylinders_position_id'], ['auto_enginecylindersposition.id']),
    )


class OriginEngine(BaseEngine, WithOrigin(Engine), Base):
    __tablename__ = 'auto_originengine'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.ForeignKeyConstraint(
            ['complectation_id', 'origin'],
            ['auto_origincomplectation.id', 'auto_origincomplectation.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['position_id', 'origin'],
            ['auto_originengineposition.id', 'auto_originengineposition.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['energy_source_id', 'origin'],
            ['auto_originenergysource.id', 'auto_originenergysource.origin'],
        ),
        sa.ForeignKeyConstraint(
            ['cylinders_position_id', 'origin'],
            ['auto_originenginecylindersposition.id', 'auto_originenginecylindersposition.origin'],
        ),
    )
