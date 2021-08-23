# coding=utf-8

from __future__ import absolute_import

import logging
from terminal.db.models import SysRoleUser
import time

import jwt
from talos.core import config, utils
from talos.core.i18n import _
from talos.core import exceptions as core_ex

from terminal.common import exceptions
from terminal.common import utils as terminal_utils
from terminal.db import resource as db_resource

CONF = config.CONF
LOG = logging.getLogger(__name__)
ACCESS_TOKEN_EXPIRES = 20 * 60
REFRESH_TOKEN_EXPIRES = 40 * 60


class SysUser(db_resource.SysUser):
    def generate_tokens(self, rid):
        roles = self.get_roles(rid)
        tokens = []
        access_token_iat = int(time.time())
        access_token_exp = access_token_iat + ACCESS_TOKEN_EXPIRES
        refresh_token_exp = access_token_iat + REFRESH_TOKEN_EXPIRES
        decoded_secret = terminal_utils.b64decode_key(CONF.jwt_signing_key)
        tokens.append({
            "expiration":
            str(access_token_exp),
            "token":
            jwt.encode(
                {
                    "sub": rid,
                    "iat": access_token_iat,
                    "type": "accessToken",
                    "clientType": "USER",
                    "exp": access_token_exp,
                    "authority": "[" + ','.join([r['id'] for r in roles]) + "]"
                },
                decoded_secret,
                "HS512",
            ).decode(),
            "tokenType":
            "accessToken"
        })
        tokens.append({
            "expiration":
            str(refresh_token_exp),
            "token":
            jwt.encode(
                {
                    "sub": rid,
                    "iat": access_token_iat,
                    "type": "refreshToken",
                    "clientType": "USER",
                    "exp": refresh_token_exp
                },
                decoded_secret,
                "HS512",
            ).decode(),
            "tokenType":
            "refreshToken"
        })
        return tokens

    def login(self, username, password):
        with self.get_session():
            if self.check_password(username, password):
                return self.generate_tokens(username)
            else:
                raise core_ex.LoginError()

    def refresh(self, token):
        with self.get_session():
            try:
                decoded_secret = terminal_utils.b64decode_key(CONF.jwt_signing_key)
                info = jwt.decode(token, key=decoded_secret, verify=True)
                if info['type'] != 'refreshToken':
                    raise core_ex.AuthError()
                return self.generate_tokens(info['sub'])
            except jwt.exceptions.ExpiredSignatureError:
                raise core_ex.AuthError()
            except jwt.exceptions.DecodeError:
                raise core_ex.AuthError()

    def get_menus(self, rid):
        with self.get_session() as session:
            menus = []
            exists = {}
            roles = self.get_roles(rid)
            for role in roles:
                for menu in SysRole(session=session).get_menus(role['id']):
                    if menu['id'] not in exists:
                        menus.append(menu)
                        exists[menu['id']] = True
            return menus

    def get_roles(self, rid):
        ref = self.get(rid)
        if ref:
            return ref['roles']
        return []

    def reset_password(self, rid, password=None):
        resource = {}
        resource['salt'] = utils.generate_salt(16)
        password = password or utils.generate_salt(16)
        resource['password'] = utils.encrypt_password(password, resource['salt'])
        before_update, after_update = self.update(rid, resource, validate=False)
        if after_update:
            after_update['password'] = password
        return after_update

    def check_password(self, rid, password):
        refs = self.list_internal({'id': rid})
        if refs:
            return utils.check_password(refs[0]['password'], password, refs[0]['salt'])
        return False

    def update_password(self, rid, password, origin_password):
        if self.check_password(rid, origin_password):
            resource = {}
            resource['salt'] = utils.generate_salt(16)
            password = password or utils.generate_salt(16)
            resource['password'] = utils.encrypt_password(password, resource['salt'])
            before_update, after_update = self.update(rid, resource, validate=False)
            return after_update
        else:
            raise exceptions.PluginError(message=_('faild to set new password: incorrect origin password'))


class SysRole(db_resource.SysRole):
    def get_users(self, rid):
        ref = self.get(rid)
        if ref:
            return ref['users']
        return []

    def _update_intersect_refs(self, rid, self_field, ref_field, resource_type, refs, session):
        old_refs = [result[ref_field] for result in resource_type(session=session).list(filters={self_field: rid})]
        create_refs = list(set(refs) - set(old_refs))
        create_refs.sort(key=refs.index)
        delete_refs = set(old_refs) - set(refs)
        if delete_refs:
            resource_type(transaction=session).delete_all(filters={
                self_field: rid,
                ref_field: {
                    'in': list(delete_refs)
                }
            })
        for ref in create_refs:
            new_ref = {}
            new_ref[self_field] = rid
            new_ref[ref_field] = ref
            resource_type(transaction=session).create(new_ref)

    def set_users(self, rid, users):
        with self.transaction() as session:
            self._update_intersect_refs(rid, 'role_id', 'user_id', db_resource.SysRoleUser, users, session)
            return self.get_users()

    def get_menus(self, rid):
        ref = self.get(rid)
        if ref:
            return ref['menus']
        return []

    def set_menus(self, rid, menus):
        with self.transaction() as session:
            self._update_intersect_refs(rid, 'role_id', 'menu_id', db_resource.SysRoleMenu, menus, session)
            return self.get_menus()


class SysMenu(db_resource.SysMenu):
    pass
