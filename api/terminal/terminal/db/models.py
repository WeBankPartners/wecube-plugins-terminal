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


class Asset(Base, DictBase):
    __tablename__ = 'asset'

    id = Column(String(36), primary_key=True)
    name = Column(String(63))
    display_name = Column(String(63))
    description = Column(String(255))
    ip_address = Column(String(36), nullable=False)
    port = Column(INTEGER(10), nullable=False)
    username = Column(String(36), nullable=False)
    password = Column(String(255), nullable=False)
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)


class SysMenu(Base, DictBase):
    __tablename__ = 'sys_menu'
    attributes = [
        'id', 'display_name', 'url', 'seq_no', 'parent', 'is_active', 'created_by', 'created_time', 'updated_by',
        'updated_time'
    ]
    summary_attributes = ['id', 'display_name', 'url', 'seq_no', 'parent', 'is_active']

    id = Column(String(36), primary_key=True, comment='主键')
    display_name = Column(String(64), comment='显示名')
    url = Column(String(255), comment='访问路径')
    seq_no = Column(INTEGER(11), server_default=text("'0'"), comment='排序号')
    parent = Column(String(36), comment='父菜单')
    is_active = Column(String(8), server_default=text("'yes'"), comment='状态')
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    roles = relationship("SysRole", secondary="sys_role_menu", back_populates="menus", uselist=True, viewonly=True)


class SysRole(Base, DictBase):
    __tablename__ = 'sys_role'
    attributes = [
        'id', 'description', 'role_type', 'is_system', 'created_by', 'created_time', 'updated_by', 'updated_time',
        'menus'
    ]
    summary_attributes = ['id', 'description', 'role_type', 'is_system']
    detail_attributes = [
        'id', 'description', 'role_type', 'is_system', 'created_by', 'created_time', 'updated_by', 'updated_time',
        'users', 'menus'
    ]

    id = Column(String(36), primary_key=True, comment='主键')
    description = Column(String(255), comment='描述')
    role_type = Column(String(32), comment='角色类型')
    is_system = Column(String(8), server_default=text("'no'"), comment='是否系统角色')
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    users = relationship("SysUser", secondary="sys_role_user", back_populates="roles", uselist=True, viewonly=True)
    menus = relationship("SysMenu", secondary="sys_role_menu", back_populates="roles", uselist=True, viewonly=True)


class SysUser(Base, DictBase):
    __tablename__ = 'sys_user'
    attributes = [
        'id', 'display_name', 'password', 'salt', 'description', 'is_system', 'created_by', 'created_time',
        'updated_by', 'updated_time'
    ]
    summary_attributes = ['id', 'display_name', 'description', 'is_system']
    detail_attributes = [
        'id', 'display_name', 'password', 'salt', 'description', 'is_system', 'created_by', 'created_time',
        'updated_by', 'updated_time', 'roles'
    ]

    id = Column(String(36), primary_key=True, comment='主键')
    display_name = Column(String(64), comment='显示名')
    password = Column(String(128), comment='加密密钥')
    salt = Column(String(36), comment='加密盐')
    description = Column(String(255), comment='描述')
    is_system = Column(String(8), server_default=text("'no'"), comment='是否系统用户')
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    roles = relationship("SysRole", secondary="sys_role_user", back_populates="users", uselist=True, viewonly=True)


class SysRoleMenu(Base, DictBase):
    __tablename__ = 'sys_role_menu'

    id = Column(BIGINT(20), primary_key=True)
    role_id = Column(ForeignKey('sys_role.id'), index=True, comment='角色id')
    menu_id = Column(ForeignKey('sys_menu.id'), index=True, comment='菜单id')
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    menu = relationship('SysMenu')
    role = relationship('SysRole')


class SysRoleUser(Base, DictBase):
    __tablename__ = 'sys_role_user'

    id = Column(BIGINT(20), primary_key=True)
    role_id = Column(ForeignKey('sys_role.id'), index=True, comment='角色id')
    user_id = Column(ForeignKey('sys_user.id'), index=True, comment='用户id')
    created_by = Column(String(36))
    created_time = Column(DateTime)
    updated_by = Column(String(36))
    updated_time = Column(DateTime)

    role = relationship('SysRole')
    user = relationship('SysUser')
