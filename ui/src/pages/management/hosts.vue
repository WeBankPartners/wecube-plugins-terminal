<template>
  <div class=" ">
    <TerminalPageTable :pageConfig="pageConfig"> </TerminalPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <div slot="passwordSlot">
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('button.password') }}:</label>
          <Input v-model="modelConfig.addRow.password" style="width:70%" type="password"></Input>
          <label v-if="modelConfig.isAdd" class="required-tip">*</label>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('button.rePassword') }}:</label>
          <Input v-model="modelConfig.addRow.confirmPassword" style="width:70%" type="password"></Input>
          <label v-if="modelConfig.isAdd" class="required-tip">*</label>
        </div>
      </div>
    </ModalComponent>
  </div>
</template>
<script>
import { getTableData, addMgmtAssets, deleteMgmtAssets, editMgmtAssets } from '@/api/server'
let tableEle = [
  {
    title: 'field.displayName',
    value: 'display_name',
    display: true
  },
  {
    title: 't_name',
    value: 'name',
    display: true
  },
  {
    title: 'button.username',
    value: 'username',
    display: true
  },
  {
    title: 'field.ip',
    value: 'ip_address', //
    display: true
  },
  {
    title: 'field.port',
    value: 'port',
    display: true
  },
  {
    title: 'description',
    value: 'description',
    display: true
  },
  {
    title: 't_created_time',
    value: 'created_time',
    display: true
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
      pageConfig: {
        CRUD: '/terminal/v1/mgmt-assets',
        researchConfig: {
          input_conditions: [
            {
              value: 'name__icontains',
              type: 'input',
              placeholder: 't_name',
              style: ''
            },
            { name: 'transmitExtraSearch', type: 'slot' }
          ],
          btn_group: [
            {
              btn_name: 'button.search',
              btn_func: 'initTableData',
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
        modalId: 'add_edit_Modal',
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
          {
            label: 'field.displayName',
            value: 'display_name',
            placeholder: 'tips.required',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'field.ip',
            value: 'ip_address',
            placeholder: 'tips.required',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            label: 'field.port',
            value: 'port',
            placeholder: 'tips.required',
            v_validate: '',
            max: 65535,
            min: 1,
            disabled: false,
            type: 'inputNumber'
          },
          {
            label: 'button.username',
            value: 'username',
            placeholder: 'tips.required',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          {
            name: 'passwordSlot',
            type: 'slot'
          },
          { label: 'description', value: 'description', placeholder: '', v_validate: '', disabled: false, type: 'text' }
        ],
        addRow: {
          name: '',
          display_name: '',
          ip_address: '',
          port: 22,
          username: '',
          password: '',
          confirmPassword: '',
          description: ''
        }
      },
      id: null,
      modelTip: {
        key: 'name',
        value: null
      }
    }
  },
  mounted () {
    this.initTableData()
  },
  methods: {
    async initTableData () {
      const params = this.$TerminalCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    add () {
      this.modelConfig.isAdd = true
      this.modelConfig.addRow.port = 22
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      if (this.modelConfig.addRow.password === '' || this.modelConfig.addRow.confirmPassword === '') {
        this.$Notice.warning({
          title: 'Warning',
          desc: this.$t('password_warning')
        })
        return
      }
      if (this.modelConfig.addRow.confirmPassword !== this.modelConfig.addRow.password) {
        this.$Notice.warning({
          title: 'Warning',
          desc: this.$t('confirm_password_error')
        })
        return
      }
      const { status, message } = await addMgmtAssets([this.modelConfig.addRow])
      if (status === 'OK') {
        this.$root.JQ('#add_edit_Modal').modal('hide')
        this.$Notice.success({
          title: 'Success',
          desc: message
        })
        this.initTableData()
      }
    },
    editF (rowData) {
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.id = rowData.id
      this.modelConfig.addRow = this.$TerminalCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      if (this.modelConfig.addRow.password === '') {
        delete this.modelConfig.addRow.password
      } else {
        if (this.modelConfig.addRow.confirmPassword === '') {
          this.$Notice.warning({
            title: 'Warning',
            desc: this.$('password_warning')
          })
          return
        }
      }
      const { status, message } = await editMgmtAssets(this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.$root.JQ('#add_edit_Modal').modal('hide')
        this.$Notice.success({
          title: 'Success',
          desc: message
        })
        this.initTableData()
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('confirm_to_delete'),
        'z-index': 1000000,
        onOk: async () => {
          const { status, message } = await deleteMgmtAssets(rowData.id)
          if (status === 'OK') {
            this.$Notice.success({
              title: 'Success',
              desc: message
            })
            this.initTableData()
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
