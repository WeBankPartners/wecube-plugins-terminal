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
          style="width: 340px"
        >
          <Option v-for="item in assertsOption" :value="item.id" :key="item.id">{{
            item.ip_address + '(' + item.name + ')'
          }}</Option>
        </Select>
        <DatePicker
          type="datetimerange"
          @on-change="changeDate"
          :placeholder="$t('t_select_datetime')"
          style="width: 300px"
        ></DatePicker>
      </div>
    </TerminalPageTable>
  </div>
</template>

<script>
import { getAssets, getTableData } from '@/api/server'
import { getCookie } from '@/pages/util/cookie'
import { byteConvert } from '@/pages/util/functools'
let tableEle = [
  {
    title: 't_asset_id',
    value: 'asset_id',
    style: { width: '200px' },
    display: true,
    render: item => {
      return (item.asset && item.asset.ip_address) || item.asset_id
    }
  },
  {
    title: 't_user',
    value: 'user',
    style: { width: '150px' },
    display: true
  },
  {
    title: 't_started_time',
    value: 'started_time',
    style: { width: '250px' },
    sortable: true,
    display: true
  },
  {
    title: 't_ended_time',
    value: 'ended_time', //
    style: { width: '250px' },
    sortable: true,
    display: true
  },
  {
    title: 't_filepath',
    value: 'filepath',
    display: true
  },
  {
    title: 't_filesize',
    value: 'filesize',
    sortable: true,
    display: true,
    style: { width: '100px' },
    render: item => {
      return byteConvert(item.filesize)
    }
  }
]
const btn = [{ btn_name: 't_operation_replay', btn_func: 'replay' }]
export default {
  name: '',
  data () {
    return {
      pageConfig: {
        CRUD: '/terminal/v1/session-records',
        researchConfig: {
          input_conditions: [
            {
              value: 'user__icontains',
              type: 'input',
              placeholder: 't_user',
              style: ''
            },
            { name: 'transmitExtraSearch', type: 'slot' }
          ],
          btn_group: [
            {
              btn_name: 'button.search',
              btn_func: 'search',
              class: 'btn-confirm-f',
              btn_icon: 'fa fa-search'
            }
          ],
          filters: {
            user__icontains: ''
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
      asset_id: '',
      assertsOption: []
    }
  },
  watch: {},
  mounted () {
    this.initTableData()
    this.initAssets()
  },
  methods: {
    async initAssets () {
      const { status, data } = await getAssets()
      if (status === 'OK') {
        this.assertsOption = data.data
      }
    },
    changeDate (val) {
      if (val[0] === '') {
        delete this.pageConfig.researchConfig.filters.started_time__gte
        delete this.pageConfig.researchConfig.filters.ended_time__lte
        return
      }
      this.pageConfig.researchConfig.filters.started_time__gte = val[0]
      this.pageConfig.researchConfig.filters.ended_time__lte = val[1]
    },
    async initTableData () {
      if (!this.asset_id) {
        delete this.pageConfig.researchConfig.filters.asset_id
      } else {
        this.pageConfig.researchConfig.filters.asset_id = this.asset_id
      }
      const params = this.$TerminalCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    replay (data) {
      localStorage.setItem('fileId', data.id)
      localStorage.setItem('replayToken', getCookie('accessToken'))
      let url = ''
      const scripts = document.getElementsByTagName('script')
      for (let i = 0; i < scripts.length; i++) {
        if (scripts[i].src.endsWith('/xtem-player/xterm-player.min.js')) {
          url = scripts[i].src
        }
      }
      const len = url.length
      url = url.substring(0, len - 31)
      window.open(url + 'replay-page.html', '_blank')
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
