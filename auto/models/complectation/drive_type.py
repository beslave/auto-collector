import sqlalchemy as sa

from auto.models.base import Base, WithOrigin


class BaseDriveType:
    id = sa.Column(sa.Integer, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)


class DriveType(BaseDriveType, Base):
    __tablename__ = 'auto_drivetype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


class OriginDriveType(BaseDriveType, WithOrigin(DriveType), Base):
    __tablename__ = 'auto_origindrivetype'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id', 'origin'),
        sa.UniqueConstraint('name', 'origin'),
    )
