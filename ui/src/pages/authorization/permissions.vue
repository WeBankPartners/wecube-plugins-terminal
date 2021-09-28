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
          <Option v-for="item in assertsOption" :value="item.id" :key="item.id">{{
            item.ip_address + '(' + item.name + ')'
          }}</Option>
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
              {{ item.ip_address + '(' + item.name + ')' }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each" v-if="showRegular()">
          <label class="col-md-2 label-name">{{ $t('t_auth_expression') }}:</label>
          <span
            ><FilterRules
              style="width:340px;display:inline-block;vertical-align: middle;"
              :needAttr="true"
              v-model="modelConfig.addRow.expression"
              :allDataModelsWithAttrs="allEntityType"
            ></FilterRules
          ></span>
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
import {
  getTableData,
  getAssets,
  getAllRolesPlatform,
  getAllRoles,
  savePermission,
  editPermissions,
  deleteTableRow,
  getAllDataModels
} from '@/api/server'
import FilterRules from '../components/filter-rules.vue'
let tableEle = [
  {
    title: 't_name',
    value: 'name',
    display: true,
    style: { width: '200px' }
  },
  {
    title: 't_asset_id',
    value: 'asset_id',
    display: true,
    render: item => {
      const res = item.assets.map(asset => {
        return asset.ip_address
      })
      return res.join('/')
    }
  },
  {
    title: 't_auth_expression',
    value: 'expression',
    display: true
  },
  {
    title: 't_roles',
    value: 'roles',
    display: true,
    render: item => {
      return item.roles.join('/')
    }
  },
  {
    title: 't_auth_upload',
    value: 'auth_upload', //
    style: { width: '100px' },
    display: true,
    render: item => {
      return item.auth_upload === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_auth_download',
    value: 'auth_download',
    style: { width: '100px' },
    display: true,
    render: item => {
      return item.auth_download === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_auth_execute',
    value: 'auth_execute',
    style: { width: '100px' },
    display: true,
    render: item => {
      return item.auth_execute === 1 ? 'TRUE' : 'FALSE'
    }
  },
  {
    title: 't_enabled',
    value: 'enabled',
    style: { width: '100px' },
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
      isPlugin: false,
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
          expression: '',
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
      rolesOption: [],
      allEntityType: []
    }
  },
  mounted () {
    this.isPlugin = window.request
    const removeRegular = this.showRegular()
    if (!removeRegular) {
      tableEle[2].display = false
    }
    this.initTableData()
    this.initAssets()
    this.initRoles()
    this.$root.JQ('#add_object_Modal').on('hidden.bs.modal', () => {
      this.modelConfig.addRow.auth_upload = 1
      this.modelConfig.addRow.auth_download = 1
      this.modelConfig.addRow.auth_execute = 1
      this.modelConfig.addRow.enabled = 1
    })
  },
  methods: {
    showRegular () {
      return !!window.request
    },
    async initAssets () {
      const { status, data } = await getAssets()
      if (status === 'OK') {
        this.assertsOption = data.data
      }
    },
    async initRoles () {
      const method = this.isPlugin ? getAllRolesPlatform : getAllRoles
      const { data, status } = await method()
      if (status === 'OK') {
        if (this.isPlugin) {
          this.rolesOption = data
        } else {
          this.rolesOption = data.data.map(item => {
            return {
              ...item,
              name: item.id,
              displayName: item.description
            }
          })
        }
      }
    },
    async getAllDataModels () {
      let { data, status } = await getAllDataModels()
      if (status === 'OK') {
        this.allEntityType = data
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
    async getRolesForModal () {
      const method = this.isPlugin ? getAllRolesPlatform : getAllRoles
      const { data, status } = await method()
      if (status === 'OK') {
        if (this.isPlugin) {
          this.modelConfig.slotConfig.rolesOption = data
          this.getAllDataModels()
        } else {
          this.modelConfig.slotConfig.rolesOption = data.data.map(item => {
            return {
              ...item,
              name: item.id,
              displayName: item.description
            }
          })
        }
      }
    },
    async add () {
      this.modelConfig.isAdd = true
      const res = await getAssets()
      if (res.status === 'OK') {
        this.modelConfig.slotConfig.assertsOption = res.data.data
      }
      await this.getRolesForModal()
      this.$root.JQ('#add_object_Modal').modal('show')
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
      await this.getRolesForModal()
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
  components: { FilterRules }
}
</script>

<style scoped lang="scss"></style>
