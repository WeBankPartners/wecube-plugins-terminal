# coding=utf-8

from __future__ import absolute_import

from talos.db.dictbase import DictBase
from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Permission(Base, DictBase):
    __tablename__ = 'permission'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    enabled = Column(TINYINT(4), nullable=False)
    auth_upload = Column(TINYINT(4), nullable=False)
    auth_download = Column(TINYINT(4), nullable=False)
    auth_execute = Column(TINYINT(4), nullable=False)
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    assets = relationship("PermissionAsset", back_populates="permission")
    roles = relationship("PermissionRole", back_populates="permission")


class PermissionAsset(Base, DictBase):
    __tablename__ = 'permission_asset'

    id = Column(BIGINT(20), primary_key=True)
    permission_id = Column(ForeignKey('permission.id'), nullable=False, index=True)
    asset_id = Column(String(36), nullable=False)

    permission = relationship('Permission', back_populates="assets")


class PermissionRole(Base, DictBase):
    __tablename__ = 'permission_role'

    id = Column(BIGINT(20), primary_key=True)
    permission_id = Column(ForeignKey('permission.id'), nullable=False, index=True)
    role = Column(String(255), nullable=False)

    permission = relationship('Permission', back_populates="roles")


class SessionRecord(Base, DictBase):
    __tablename__ = 'session_record'

    id = Column(BIGINT(20), primary_key=True)
    asset_id = Column(String(36), nullable=False)
    filepath = Column(String(255), nullable=False)
    user = Column(String(36), nullable=False)
    started_time = Column(DateTime, nullable=False)
    ended_time = Column(DateTime)


class TransferRecord(Base, DictBase):
    __tablename__ = 'transfer_record'

    id = Column(BIGINT(20), primary_key=True)
    asset_id = Column(String(36), nullable=False)
    filepath = Column(String(255), nullable=False)
    filesize = Column(BIGINT(20), nullable=False)
    user = Column(String(36), nullable=False)
    operation_type = Column(String(36), nullable=False)
    started_time = Column(DateTime, nullable=False)
    ended_time = Column(DateTime)
    status = Column(String(36))
