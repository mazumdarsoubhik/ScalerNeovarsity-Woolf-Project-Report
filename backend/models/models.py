from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AuthenticationModes(Base):
    """
        Class for authentication_modes db table
    """

    __tablename__ = 'authentication_modes'

    modes = Column(String(100), primary_key=True, nullable=False)


class Permission(Base):
    """
        Class for permission db table
    """

    __tablename__ = 'permission'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)


class Roles(Base):
    """
        Class for roles db table
    """

    __tablename__ = 'roles'

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    can_edit = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)
    date_added = Column(DateTime, nullable=False)
    roles_permission_association = relationship("RolesPermissionAssociation")


class RolesPermissionAssociation(Base):
    """
        Class for roles_permission_association db table
    """

    __tablename__ = 'roles_permission_association'

    id = Column(String(36), primary_key=True, nullable=False)
    roles_id = Column(String(36), ForeignKey('roles.id'), nullable=False)
    permission_id = Column(String(36), ForeignKey('permission.id'), nullable=False)
    permission = relationship("Permission")


class User(Base):
    """
        Class for user db table
    """

    __tablename__ = 'user'

    username = Column(String(200), primary_key=True, nullable=False)
    password = Column(String(200), nullable=True)
    last_login_timestamp = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False)
    invalid_login_attempts = Column(Integer, nullable=False)
    date_added = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    authentication_mode = Column(String(100), ForeignKey("authentication_modes.modes"), nullable=False)
    role = Column(String(36), ForeignKey('roles.id'), nullable=False)
    user_role = relationship("Roles")
