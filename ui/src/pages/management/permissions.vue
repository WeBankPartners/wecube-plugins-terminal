<template>
  <div class=" ">
    <TerminalPageTable :pageConfig="pageConfig">
      <div slot="extraSearch">
        <Select
          v-model="asset_id"
          filterable
          clearable
          @on-clear="initTableData"
          :placeholder="$t('t_asset_id')"
          style="width:340px"
        >
          <Option v-for="item in assertsOption" :value="item.id" :key="item.id">{{ item.ip_address }}</Option>
        </Select>
        <Select
          v-model="roles_id"
          filterable
          clearable
          @on-clear="initTableData"
          :placeholder="$t('t_roles')"
          style="width:340px"
        >
          <Option v-for="item in rolesOption" :value="item.name" :key="item.name">{{ item.displayName }}</Option>
        </Select>
      </div>
    </TerminalPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <div slot="permissionConfig" class="extentClass">
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_asset_id') }}:</label>
          <Select v-model="modelConfig.addRow.assets" multiple filterable style="width:340px">
            <Option v-for="item in modelConfig.slotConfig.assertsOption" :value="item.id" :key="item.id">
              {{ item.ip_address }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_roles') }}:</label>
          <Select v-model="modelConfig.addRow.roles" multiple filterable style="width:340px">
            <Option v-for="item in modelConfig.slotConfig.rolesOption" :value="item.name" :key="item.name">
              {{ item.displayName }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_auth_upload') }}:</label>
          <Checkbox v-model="modelConfig.addRow.auth_upload" :true-value="tValue" :false-value="fValue"></Checkbox>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_auth_download') }}:</label>
          <Checkbox v-model="modelConfig.addRow.auth_download" :true-value="tValue" :false-value="fValue"></Checkbox>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_auth_execute') }}:</label>
          <Checkbox v-model="modelConfig.addRow.auth_execute" :true-value="tValue" :false-value="fValue"></Checkbox>
        </div>
        <hr />
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('t_enabled') }}:</label>
          <Checkbox v-model="modelConfig.addRow.enabled" :true-value="tValue" :false-value="fValue"></Checkbox>
        </div>
      </div>
    </ModalComponent>
  </div>
</template>

<script>
import { getTableData, getAssets, getAllRoles, savePermission, editPermissions, deleteTableRow } from '@/api/server'
let tableEle = [
  {
    title: 't_name',
    value: 'name',
    style: { width: '100px' },
    display: true
  },
  {
    title: 't_asset_id',
    value: 'asset_id',
    style: { width: '400px' },
    display: true,
    render: item => {
      const res = item.assets.map(asset => {
        return asset.ip_address
      })
      return res.join('/')
    }
  },
  {
    title: 't_roles',
    value: 'roles',
    style: { width: '300px' },
    display: true,
    render: item => {
      return item.roles.join('/')
    }
  },
  {
    title: 't_auth_upload',
    value: 'auth_upload', //
    style: { width: '300px' },
    display: true,
    render: item => {
      return item.auth_upload === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_auth_download',
    value: 'auth_download',
    display: true,
    render: item => {
      return item.auth_download === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_auth_execute',
    value: 'auth_execute',
    display: true,
    render: item => {
      return item.auth_execute === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_enabled',
    value: 'enabled',
    display: true,
    render: item => {
      return item.enabled === 1 ? 'YES' : 'NO'
    }
  }
]
const btn = [
  { btn_name: 'button.edit', btn_func: 'editF' },
  { btn_name: 'button.remove', btn_func: 'deleteConfirmModal' }
]
export default {
  name: '',
  data () {
    return {
      tValue: 1,
      fValue: 0,
      pageConfig: {
        CRUD: '/terminal/v1/permissions',
        researchConfig: {
          input_conditions: [
            {
              value: 'name__icontains',
              type: 'input',
              placeholder: 't_name',
              style: ''
            }
          ],
          btn_group: [
            {
              btn_name: 'button.search',
              btn_func: 'search',
              class: 'btn-confirm-f',
              btn_icon: 'fa fa-search'
            },
            { btn_name: 'button.add', btn_func: 'add', class: 'btn-cancel-f', btn_icon: 'fa fa-plus' }
          ],
          filters: {
            name__icontains: ''
          }
        },
        table: {
          tableData: [],
          tableEle: tableEle,
          // filterMoreBtn: 'filterMoreBtn',
          primaryKey: 'guid',
          btn: btn,
          pagination: this.pagination,
          handleFloat: true
        },
        pagination: {
          total: 0,
          page: 1,
          size: 10
        }
      },
      modelConfig: {
        modalId: 'add_object_Modal',
        modalTitle: 'button.add',
        isAdd: true,
        config: [
          {
            label: 't_name',
            value: 'name',
            placeholder: 'tips.required',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          { name: 'permissionConfig', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          assets: [],
          roles: [],
          auth_upload: 1,
          auth_download: 1,
          auth_execute: 1,
          enabled: 1
        },
        slotConfig: {
          assertsOption: [],
          rolesOption: []
        }
      },
      modelTip: {
        key: 'name',
        value: null
      },
      id: null,
      asset_id: '',
      assertsOption: [],
      roles_id: '',
      rolesOption: []
    }
  },
  mounted () {
    this.initTableData()
    this.initAssets()
    this.initRoles()
  },
  methods: {
    async initAssets () {
      const { status, data } = await getAssets()
      if (status === 'OK') {
        this.assertsOption = data.data
      }
    },
    async initRoles () {
      const { status, data } = await getAllRoles()
      if (status === 'OK') {
        this.rolesOption = data
      }
    },
    async initTableData () {
      if (!this.asset_id) {
        delete this.pageConfig.researchConfig.filters['assets.asset_id']
      } else {
        this.pageConfig.researchConfig.filters['assets.asset_id'] = this.asset_id
      }
      if (!this.roles_id) {
        delete this.pageConfig.researchConfig.filters['roles.role']
      } else {
        this.pageConfig.researchConfig.filters['roles.role'] = this.roles_id
      }
      const params = this.$TerminalCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async add () {
      const res = await getAssets()
      if (res.status === 'OK') {
        this.modelConfig.slotConfig.assertsOption = res.data.data
      }
      const { status, data } = await getAllRoles()
      if (status === 'OK') {
        this.modelConfig.slotConfig.rolesOption = data
        this.$root.JQ('#add_object_Modal').modal('show')
      }
    },
    async addPost () {
      const { status } = await savePermission([this.modelConfig.addRow])
      if (status === 'OK') {
        this.$Notice.success({
          title: 'Success',
          desc: 'Success'
        })
        this.$root.JQ('#add_object_Modal').modal('hide')
        this.initTableData()
      }
    },
    async editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$TerminalCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.modelConfig.addRow.assets = rowData.assets.map(item => item.id)
      this.modelConfig.addRow.roles = rowData.roles
      const res = await getAssets()
      if (res.status === 'OK') {
        this.modelConfig.slotConfig.assertsOption = res.data.data
      }
      const { status, data } = await getAllRoles()
      if (status === 'OK') {
        this.modelConfig.slotConfig.rolesOption = data
      }
      this.$root.JQ('#add_object_Modal').modal('show')
    },
    async editPost () {
      const { status } = await editPermissions(this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.$Notice.success({
          title: 'Success',
          desc: 'Success'
        })
        this.$root.JQ('#add_object_Modal').modal('hide')
        this.initTableData()
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('delete_confirm') + rowData.name,
        'z-index': 1000000,
        onOk: async () => {
          const { status, message } = await deleteTableRow(this.pageConfig.CRUD, rowData.id)
          if (status === 'OK') {
            this.initTableData()
            this.$Notice.success({
              title: 'Success',
              desc: message
            })
          }
        },
        onCancel: () => {}
      })
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
