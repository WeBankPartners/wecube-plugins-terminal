<template>
  <Row>
    <Col span="7" offset="1">
      <Card>
        <p slot="title" class="permission-management-p">
          <span>{{ $t('user') }}</span>
          <Button icon="ios-add" type="dashed" size="small" @click="openAddUserModal">{{ $t('add_user') }}</Button>
        </p>
        <div class="tagContainers">
          <Tag
            v-for="item in users"
            :key="item.id"
            :name="item.id"
            :color="item.color"
            :checked="item.checked"
            checkable
            :fade="false"
            @on-change="handleUserClick"
          >
            <span :title="` ${item.display_name} ( ${item.description} ) `">{{
              ` ${item.display_name} ( ${item.description} ) `
            }}</span>
            <span v-if="users.length > 1" style="float: right" @click="resetPassword($event, item)">
              <Icon size="20" type="ios-unlock-outline" />
            </span>
            <span v-if="users.length > 1" style="float: right; color: red" @click="deleteUser($event, item)">
              <Icon size="20" type="ios-trash-outline" />
            </span>
          </Tag>
        </div>
      </Card>
    </Col>
    <Col span="7" offset="1" style="margin-left: 20px">
      <Card>
        <p slot="title" class="permission-management-p">
          <span>{{ $t('role') }}</span>
          <Button icon="ios-add" type="dashed" size="small" @click="openAddRoleModal">{{ $t('add_role') }}</Button>
        </p>
        <div class="tagContainers">
          <div class="role-item" v-for="item in roles" :key="item.id">
            <Tag
              :name="item.id"
              :color="item.color"
              :checked="item.checked"
              checkable
              :fade="false"
              @on-change="handleRoleClick"
            >
              <span :title="item.description">{{ item.description }}</span>
              <span v-if="item.id !== 'SUPER_ADMIN'" style="float: right; color: red" @click="deleteRole($event, item)">
                <Icon size="20" type="ios-trash-outline" />
              </span>
            </Tag>
            <Button icon="md-person" type="dashed" size="small" @click="openUserManageModal(item.id)">{{
              $t('user')
            }}</Button>
          </div>
        </div>
      </Card>
    </Col>
    <Col span="7" offset="1" style="margin-left: 20px">
      <Card>
        <p slot="title">{{ $t('menus_management') }}</p>
        <div class="tagContainers">
          <Spin size="large" fix v-if="spinShow"></Spin>
          <Tree :data="menus" show-checkbox @on-check-change="handleMenuTreeCheck"></Tree>
        </div>
      </Card>
    </Col>
    <Modal v-model="addRoleModalVisible" :title="$t('add_role')" @on-ok="addRole" @on-cancel="cancel">
      <Input v-model="addedRoleValue" :placeholder="$t('username_input_placeholder')" />
    </Modal>
    <Modal v-model="addUserModalVisible" :title="$t('add_user')" @on-ok="addUser" @on-cancel="cancel">
      <Form class="validation-form" ref="addedUserForm" :model="addedUser" label-position="left" :label-width="100">
        <FormItem :label="$t('username')" prop="userId">
          <Input v-model="addedUser.id" />
        </FormItem>
        <FormItem :label="$t('fullname')" prop="display_name">
          <Input v-model="addedUser.display_name" />
        </FormItem>
        <FormItem :label="$t('description')" prop="description">
          <Input v-model="addedUser.description" />
        </FormItem>
      </Form>
    </Modal>
    <Modal v-model="userManageModal" width="700" :title="$t('edit_user')" @on-ok="confirmUser" @on-cancel="confirmUser">
      <Transfer
        :titles="transferTitles"
        :list-style="transferStyle"
        :data="allUsersForTransfer"
        :target-keys="usersKeyBySelectedRole"
        :render-format="renderUserNameForTransfer"
        @on-change="handleUserTransferChange"
        filterable
      ></Transfer>
    </Modal>
    <Modal
      v-model="showPassword"
      :title="$t('copy_password')"
      @on-ok="showPassword = false"
      @on-cancel="showPassword = false"
    >
      <span>{{ newResetPassword }}</span>
    </Modal>
  </Row>
</template>
<script>
import {
  getAllUsers,
  getAllRoles,
  resetPassword,
  getAllMenus,
  deleteUser,
  deleteRole,
  getRolesByUser,
  getUsersByRole,
  addRole,
  addUser,
  getPermissionsByRole,
  getPermissionsByUser,
  addUsersToRole,
  addMenusToRole
} from '@/api/server.js'

import { MENUS } from '@/const/menus.js'

export default {
  data () {
    return {
      allCiTypes: [],
      ciTypesWithAccessControlledAttr: {},
      users: [],
      roles: [],
      menus: [],
      dataPermissionDisabled: false,
      menusForEdit: [],
      permissionEntryPoints: [],
      permissionEntryPointsForEdit: [],
      permissionEntryPointsBackup: [],
      addRoleModalVisible: false,
      addUserModalVisible: false,
      addedRoleValue: '',
      userManageModal: false,
      permissionManageModal: false,
      usersKeyBySelectedRole: [],
      allUsersForTransfer: [],
      selectedRole: null,
      transferTitles: [
        this.$t('permission_management_unselected_user'),
        this.$t('permission_management_selected_user')
      ],
      // currentRoleId: 0,
      currentRoleName: null,
      allMenusOriginResponse: [],
      transferStyle: { width: '300px' },
      currentRoleCiTypeId: '',
      addedUser: {
        id: '',
        display_name: '',
        description: ''
      },
      spinShow: false,
      showPassword: false,
      newResetPassword: ''
    }
  },
  computed: {},
  methods: {
    async resetPassword (event, user) {
      event.stopPropagation()
      this.$Modal.confirm({
        title: this.$t('reset_password'),
        'z-index': 1000000,
        onOk: async () => {
          const { status, data } = await resetPassword(user.id)
          if (status === 'OK') {
            this.newResetPassword = data.password
            this.showPassword = true
          }
        },
        onCancel: () => {}
      })
    },
    async deleteUser (event, item) {
      event.stopPropagation()
      this.$Modal.confirm({
        title: this.$t('confirm_to_delete'),
        'z-index': 1000000,
        onOk: async () => {
          let { status, message } = await deleteUser(item.id)
          if (status === 'OK') {
            this.$Notice.success({
              title: this.$t('success'),
              desc: message
            })
            this.getAllUsers()
          }
        },
        onCancel: () => {}
      })
    },
    async deleteRole (event, item) {
      event.stopPropagation()
      this.$Modal.confirm({
        title: this.$t('confirm_to_delete'),
        'z-index': 1000000,
        onOk: async () => {
          let { status, message } = await deleteRole(item.id)
          if (status === 'OK') {
            this.$Notice.success({
              title: this.$t('success'),
              desc: message
            })
            this.getAllRoles()
          }
        },
        onCancel: () => {}
      })
    },
    renderUserNameForTransfer (item) {
      return item.label
    },
    openPermissionManageModal (roleCiTypeId) {
      this.currentRoleCiTypeId = roleCiTypeId
      this.permissionManageModal = true
      this.getAttrPermissions()
    },
    async handleUserTransferChange (newTargetKeys, direction, moveKeys) {
      let { status, message } = await addUsersToRole(this.selectedRole, newTargetKeys)
      if (status === 'OK') {
        this.$Notice.success({
          title: this.$t('success'),
          desc: message
        })
        this.usersKeyBySelectedRole = newTargetKeys
      }
    },
    async addRole () {
      if (this.addedRoleValue === '') {
        this.$Notice.warning({
          title: 'Warning',
          desc: this.$t('role_name_is_required')
        })
        return
      }
      let { status, message } = await addRole([
        {
          id: this.addedRoleValue,
          description: this.addedRoleValue
        }
      ])
      if (status === 'OK') {
        this.$Notice.success({
          title: this.$t('success'),
          desc: message
        })
        this.getAllUsers()
        this.getAllRoles()
        this.getAllMenus()
      }
    },
    async addUser () {
      if (this.addedUser.id === '') {
        this.$Notice.warning({
          title: 'Warning',
          desc: this.$t('role_name_is_required')
        })
        return
      }
      let { status, data, message } = await addUser([this.addedUser])
      if (status === 'OK') {
        this.$Notice.success({
          title: this.$t('success'),
          desc: message
        })
        this.$Modal.info({
          title: this.$t('copy_password'),
          content: data[0].password
        })
        this.getAllUsers()
        this.getAllRoles()
        this.getAllMenus()
      }
    },
    async getPermissions (queryAfterEditing, checked, roleOrUser, byUser = false) {
      if (checked) {
        const method = byUser ? getPermissionsByUser : getPermissionsByRole
        let permissions = await method(roleOrUser)
        this.spinShow = false
        if (queryAfterEditing) {
          this.permissionEntryPointsForEdit = []
          this.menusPermissionSelected(this.menusForEdit, permissions.data)
        } else {
          this.permissionEntryPoints = []
          this.menusPermissionSelected(this.menus, permissions.data)
        }
      } else {
        if (queryAfterEditing) {
          this.menusPermissionSelected(this.menusForEdit)
        } else {
          this.menusPermissionSelected(this.menus)
        }
      }
    },
    async handleUserClick (checked, name) {
      this.spinShow = true
      this.currentRoleName = null
      this.dataPermissionDisabled = true
      this.users.forEach(_ => {
        _.checked = false
        if (name === _.id) {
          _.checked = checked
        }
      })
      let { status, data } = await getRolesByUser(name)
      let roles = []
      if (status === 'OK') {
        this.roles.forEach(_ => {
          _.checked = false
          const found = data.find(item => item.id === _.id)
          if (found) {
            roles.push(found.id)
            _.checked = checked
          }
          this.menus = this.menusResponseHandeler(this.allMenusOriginResponse)
        })
        this.getPermissions(false, checked, name, true)
      }
    },
    async getAllUsers () {
      let { status, data } = await getAllUsers()
      if (status === 'OK') {
        this.users = data.data.map(_ => {
          return {
            ..._,
            checked: false,
            color: '#5cadff'
          }
        })
      }
    },
    openAddRoleModal () {
      this.addedRoleValue = ''
      this.addRoleModalVisible = true
    },
    openAddUserModal () {
      this.addedUser = {
        id: '',
        display_name: '',
        description: ''
      }
      this.addUserModalVisible = true
    },

    menusPermissionSelected (allMenus, menusPermissions = []) {
      allMenus.forEach(_ => {
        _.children.forEach(m => {
          const subMenu = menusPermissions.find(n => m.id === n.id)
          m.checked = !!subMenu
        })
        _.indeterminate = false
        _.checked = false
      })
    },

    async handleRoleClick (checked, rolename) {
      this.spinShow = true
      // this.currentRoleId = id;
      this.currentRoleName = rolename
      this.dataPermissionDisabled = false
      this.menus = this.menusResponseHandeler(this.allMenusOriginResponse, false)
      this.roles.forEach(_ => {
        _.checked = false
        if (rolename === _.id) {
          _.checked = checked
        }
      })
      let { status, data } = await getUsersByRole(rolename)
      if (status === 'OK') {
        this.users.forEach(_ => {
          _.checked = false
          const found = data.find(item => item.id === _.id)
          if (found) {
            _.checked = checked
          }
        })
      }
      this.getPermissions(false, checked, rolename)
    },
    async handleMenuTreeCheck (allChecked) {
      let menuCodes = new Set()
      allChecked.forEach(item => {
        const children = item.children
        if (children) {
          children.forEach(child => {
            menuCodes.add(child.id)
          })
        } else {
          menuCodes.add(item.id)
        }
      })
      const { status, message } = await addMenusToRole(this.currentRoleName, Array.from(menuCodes))
      if (status === 'OK') {
        this.$Notice.success({
          title: this.$t('success'),
          desc: message
        })
      }
      this.getPermissions(true, true, this.currentRoleName)
    },
    async getAllRoles () {
      let { status, data } = await getAllRoles()
      if (status === 'OK') {
        this.roles = data.data.map(_ => {
          return {
            ..._,
            checked: false,
            color: 'success'
          }
        })
      }
    },
    menusResponseHandeler (data, disabled = true) {
      let menus = []
      data.forEach(_ => {
        if (!_.parent) {
          let menuObj = MENUS.find(m => m.code === _.id)
          if (menuObj) {
            menus.push({
              ..._,
              title: this.$lang === 'zh-CN' ? menuObj.cnName : menuObj.enName,
              id: _.id,
              expand: true,
              checked: false,
              children: [],
              disabled
            })
          }
        }
      })
      data.forEach(_ => {
        if (_.parent) {
          let menuObj = MENUS.find(m => m.code === _.id)
          menus.forEach(h => {
            if (_.parent === h.id) {
              h.children.push({
                ..._,
                title: menuObj ? (this.$lang === 'zh-CN' ? menuObj.cnName : menuObj.enName) : _.display_name,
                id: _.id,
                expand: true,
                checked: false,
                disabled
              })
            }
          })
        }
      })
      return menus
    },
    async getAllMenus () {
      let { status, data } = await getAllMenus()
      if (status === 'OK') {
        this.allMenusOriginResponse = data.data
        this.menus = this.menusResponseHandeler(data.data)
        this.menusForEdit = this.menusResponseHandeler(data.data, false)
      }
    },
    async openUserManageModal (rolename) {
      this.usersKeyBySelectedRole = []
      this.allUsersForTransfer = []
      this.selectedRole = rolename
      let { status, data } = await getUsersByRole(rolename)
      if (status === 'OK') {
        this.usersKeyBySelectedRole = data.map(_ => _.id)
      }
      this.allUsersForTransfer = this.users.map(_ => {
        return {
          key: _.id,
          userId: _.id,
          label: ` ${_.display_name} ( ${_.description} ) `
        }
      })
      this.userManageModal = true
    },
    cancel () {},
    confirmUser () {
      if (this.currentRoleName) {
        this.handleRoleClick(true, this.currentRoleName)
      }
    }
  },
  created () {
    this.getAllUsers()
    this.getAllRoles()
    this.getAllMenus()
  }
}
</script>

<style lang="scss" scoped>
.tagContainers-auth {
  overflow: auto;
  height: calc(100vh - 310px);
}
.tagContainers {
  overflow: auto;
  height: calc(100vh - 220px);
}
.ivu-tag {
  display: block;
  border: #515a61 1px dashed !important;
  .ivu-tag-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
  }
}

.role-item {
  .ivu-tag {
    display: inline-block;
    width: 65%;
  }
}
.data-permissions {
  width: 100%;
  height: 30px;
  border: 1px dashed gray;
  padding-left: 5px;
  padding-right: 5px;
  border-radius: 5px;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;

  & > span {
    flex: 1;
    margin-right: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &:hover {
    background-color: rgb(227, 231, 235);
  }
}
.ciTypes-options {
  float: right;
  line-height: 30px;
}
.ciTypes {
  float: left;
  line-height: 30px;
}
.ciTypes-options {
  .ivu-checkbox-indeterminate .ivu-checkbox-inner {
    background-color: #4ee643;
  }
  .ivu-checkbox-disabled.ivu-checkbox-checked .ivu-checkbox-inner {
    background-color: #5384ff;
  }
}
.permission-management-p {
  align-items: center;
  display: flex;
  height: 24px;
  span {
    margin-right: 5px;
  }
}
.batch-operation {
  padding-bottom: 0 5px 8px 5px;
  margin-bottom: 18px;
  border-bottom: 1px solid #5384ff;
}
.batch-operation-btn {
  text-align: right;
  padding-top: 8px;
  margin-top: 8px;
  border-top: 1px solid #5384ff;
}
</style>
