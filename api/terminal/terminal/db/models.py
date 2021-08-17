# coding=utf-8

from __future__ import absolute_import

from talos.db.dictbase import DictBase
from sqlalchemy import Column, DateTime, ForeignKey, String, text, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Permission(Base, DictBase):
    __tablename__ = 'permission'
    attributes = [
        'id', 'name', 'description', 'enabled', 'auth_upload', 'auth_download', 'auth_execute', 'expression',
        'created_by', 'created_time', 'updated_by', 'updated_time', 'assets', 'roles'
    ]

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    enabled = Column(TINYINT(4), nullable=False)
    auth_upload = Column(TINYINT(4), nullable=False)
    auth_download = Column(TINYINT(4), nullable=False)
    auth_execute = Column(TINYINT(4), nullable=False)
    expression = Column(Text())
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    assets = relationship("PermissionAsset", back_populates="permission", uselist=True)
    roles = relationship("PermissionRole", back_populates="permission", uselist=True)


class PermissionAsset(Base, DictBase):
    __tablename__ = 'permission_asset'
    summary_attributes = ['asset_id']

    id = Column(BIGINT(20), primary_key=True)
    permission_id = Column(ForeignKey('permission.id'), nullable=False, index=True)
    asset_id = Column(String(36), nullable=False)

    permission = relationship('Permission', back_populates="assets")


class PermissionRole(Base, DictBase):
    __tablename__ = 'permission_role'
    summary_attributes = ['role']

    id = Column(BIGINT(20), primary_key=True)
    permission_id = Column(ForeignKey('permission.id'), nullable=False, index=True)
    role = Column(String(255), nullable=False)

    permission = relationship('Permission', back_populates="roles")


class SessionRecord(Base, DictBase):
    __tablename__ = 'session_record'

    id = Column(BIGINT(20), primary_key=True)
    asset_id = Column(String(36), nullable=False)
    filepath = Column(String(255), nullable=False)
    filesize = Column(BIGINT(20), nullable=False)
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
    message = Column(String(255))


class Bookmark(Base, DictBase):
    __tablename__ = 'bookmark'
    attributes = [
        'id', 'name', 'description', 'expression', 'created_by', 'created_time', 'updated_by', 'updated_time', 'roles'
    ]

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"))
    expression = Column(String(512), nullable=False)
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    roles = relationship("BookmarkRole", back_populates="bookmark", uselist=True)


class BookmarkRole(Base, DictBase):
    __tablename__ = 'bookmark_roles'

    id = Column(BIGINT(20), primary_key=True)
    bookmark_id = Column(ForeignKey('bookmark.id', ondelete='CASCADE'), index=True)
    type = Column(String(36), nullable=False)
    role = Column(String(255), nullable=False)

    bookmark = relationship('Bookmark')


class JumpServer(Base, DictBase):
    __tablename__ = 'jump_server'

    id = Column(String(36), primary_key=True)
    name = Column(String(63), nullable=True)
    scope = Column(String(512), nullable=True)
    ip_address = Column(String(36), nullable=False)
    port = Column(INTEGER(10), nullable=False)
    username = Column(String(36), nullable=False)
    password = Column(String(255), nullable=False)
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)
