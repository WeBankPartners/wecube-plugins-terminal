<template>
  <div>
    <Row>
      <Col span="6" v-if="showHostList">
        <div class="hide-icon-left">
          <Icon type="ios-arrow-dropleft" color="#2d8cf0" @click="hideHost" size="20" />
        </div>
        <div @mouseenter="mouseenter('showHideIcon')" @mouseleave="mouseleave('showHideIcon')">
          <Card>
            <div slot="title">
              <span style="line-height: 19px">
                {{ $t('t_asset_id') }}
              </span>
            </div>
            <div class="container-host">
              <Tabs :value="currentHostTab" :animated="false" @on-click="changeHostTabs">
                <TabPane :label="$t('t_default')" name="default"></TabPane>
                <TabPane v-if="showRegular()" :label="$t('t_favorites')" name="favorites">
                  <Form :label-width="80">
                    <FormItem :label="$t('t_favorites')">
                      <Select
                        clearable
                        @on-clear="clearSelectedCollectionId"
                        v-model="selectedCollectionId"
                        @on-open-change="favoritesList"
                        @on-change="changeCollections"
                        filterable
                      >
                        <Option v-for="item in favoritesLists" :value="item.id" :key="item.id" :label="item.name">
                          <span>{{ item.name }}</span>
                          <span v-if="item.is_owner" style="float:right;">
                            <Button
                              icon="ios-trash"
                              type="error"
                              size="small"
                              @click="showDeleteConfirm(item)"
                            ></Button>
                          </span>
                          <span v-if="item.is_owner" style="float:right;margin-right: 10px">
                            <Button
                              icon="ios-build"
                              type="primary"
                              @click="openCollectionModal(false, item)"
                              size="small"
                            ></Button>
                          </span>
                        </Option>
                      </Select>
                    </FormItem>
                  </Form>
                </TabPane>
                <TabPane v-if="showRegular()" :label="$t('t_regular_expression')" name="regular_expression">
                  <span v-if="showFilterRules">
                    <FilterRules
                      style="display:inline-block;vertical-align: middle;padding:0"
                      class="col-md-12"
                      :needAttr="true"
                      v-model="expressionPath"
                      :allDataModelsWithAttrs="allEntityType"
                    ></FilterRules>
                  </span>

                  <div style="display:flex;justify-content: space-around;margin:12px">
                    <Button
                      :disabled="expressionPath === ''"
                      type="primary"
                      icon="ios-search"
                      @click="getAssetsByExpression"
                      >{{ $t('button.search') }}</Button
                    >
                    <Button type="warning" icon="ios-star-outline" @click="openCollectionModal(true, null)">{{
                      $t('t_to_be_favorites')
                    }}</Button>
                  </div>
                </TabPane>
              </Tabs>
              <div style="margin-bottom:8px">
                <Input
                  v-model="searchHost"
                  :placeholder="$t('t_search_host')"
                  @on-enter="filterHost"
                  class="search-input"
                />
                <Button type="primary" @click="filterHost" style="width: 70px;">{{ $t('button.search') }}</Button>
              </div>
              <template v-if="hostInfo.length > 0">
                <div style="margin-bottom:8px;display: flex;justify-content: space-between;">
                  <span>{{ $t('total') }}{{ hostInfo.length }}{{ $t('items') }}</span>
                  <Page
                    style="display: inline-block;vertical-align: bottom;"
                    :page-size="pageSize"
                    :current="current"
                    @on-change="pageChange"
                    :total="hostInfo.length"
                    simple
                  />
                  <span>{{ pageSize }}{{ $t('page') }}</span>
                </div>
                <Collapse>
                  <template v-for="host in hostInfoToShow">
                    <Panel :name="host.ip_address" :key="host.ip_address">
                      <div class="diyTitle">
                        {{ host.ip_address }}<span style="color:#2d8cf0">[{{ host.username }}]</span>{{ host.name }}
                      </div>
                      <template>
                        <Tooltip content="Console" :delay="500" style="float:right">
                          <i
                            disabled
                            class="fa fa-terminal operation-icon-terminal"
                            @click.stop="openTerminal(host)"
                            aria-hidden="true"
                          >
                          </i>
                        </Tooltip>
                      </template>
                      <div slot="content">
                        <div class="host-content">
                          <span class="host-content-title">id:</span>
                          <span>{{ host.id }}</span>
                        </div>
                        <div class="host-content">
                          <span class="host-content-title">name:</span>
                          <span>{{ host.name }}</span>
                        </div>
                        <div class="host-content">
                          <span class="host-content-title">display_name:</span>
                          <span style="word-break: break-all;">{{ host.display_name }}</span>
                        </div>
                      </div>
                    </Panel>
                  </template>
                </Collapse>
              </template>
              <template v-else>
                <div style="text-align:center;color:#969696;font-size:12px">
                  {{ $t('t_no_data') }}
                </div>
              </template>
            </div>
          </Card>
        </div>
      </Col>
      <Col :span="showHostList ? 18 : 24">
        <div
          v-if="!showHostList"
          @mouseenter="mouseenter('showDisplayIcon')"
          @mouseleave="mouseleave('showDisplayIcon')"
          style="width: 20px;background:#fafafa;display:inline-block;height:calc(100vh - 130px)"
        >
          <div class="hide-icon-right">
            <Icon @click="showHost" color="#2d8cf0" type="ios-arrow-dropright" size="20" />
          </div>
        </div>
        <div class="container-height" style="display:inline-block;vertical-align: top;">
          <div>
            <Tabs
              type="card"
              closable
              :animated="false"
              @on-click="clickTab"
              @on-tab-remove="handleTabRemove"
              :value="activeTab"
            >
              <template v-for="tab in terminalTabs">
                <TabPane :label="tab.showName" :name="tab.showName" :key="tab.uniqueCode">
                  <div :style="{ height: consoleConfig.terminalH + 'px', 'overflow-y': 'auto', 'margin-right': '7px' }">
                    <Terminal
                      :ref="tab.uniqueCode"
                      :host="tab"
                      :sendHostSet="sendHostSet"
                      :consoleConfig="consoleConfig"
                      @exectDangerousCmd="exectDangerousCmd"
                      @cancelDangerousCmd="cancelDangerousCmd"
                    ></Terminal>
                    <Button v-if="!showCmd" @click="sendForMulti">{{ $t('t_terminal_interaction') }}</Button>
                  </div>
                </TabPane>
              </template>
            </Tabs>
          </div>
          <div v-if="showCmd">
            <div style="margin:8px">
              <Button @click="cancelTerminalInteraction" type="warning" icon="md-exit">{{
                $t('t_cancel_terminal_interaction')
              }}</Button>
              <Tooltip content="Here is the prompt text">
                <Icon type="ios-help-circle-outline" />
                <div slot="content">
                  <div>{{ $t('t_cmd_tip1') }}</div>
                  <div>{{ $t('t_cmd_tip2') }}</div>
                  <div>{{ $t('t_cmd_tip3') }}</div>
                  <div>{{ $t('t_cmd_tip4') }}</div>
                  <div>{{ $t('t_cmd_tip5') }}</div>
                  <div>{{ $t('t_cmd_tip6') }}</div>
                </div>
              </Tooltip>
              <Checkbox :value="sendForAll" @on-change="switchAllSelect" style="font-weight: 600;">
                ALL
              </Checkbox>
              <CheckboxGroup v-model="sendHostSet" @on-change="switchCheck" style="display:inline-block">
                <template v-for="tab in terminalTabs">
                  <Checkbox :label="tab.uniqueCode" :name="tab.uniqueCode" :key="tab.uniqueCode">
                    <span>{{ tab.showName }}</span>
                  </Checkbox>
                </template>
              </CheckboxGroup>
              <Button
                :disabled="!selectedCmd"
                @click="sendHistoryCmd"
                type="primary"
                style="float:right;margin:0 16px"
                >{{ $t('t_send') }}</Button
              >
              <Select v-model="selectedCmd" style="float:right; width:200px" placeholder="history cmd">
                <Option v-for="item in historyCmd" :value="item.label" :key="item.value">{{ item.label }}</Option>
              </Select>
            </div>
            <Input
              v-model="uniteCmd"
              type="textarea"
              :autosize="{ minRows: 5, maxRows: 16 }"
              @keyup.enter.exact.native.prevent="sendCmd"
              @keyup.38.exact.native="upCmd"
              @keyup.40.exact.native="downCmd"
              @keyup.alt.enter.exact.native="warpCmd"
              placeholder="Enter something..."
            />
          </div>
        </div>
      </Col>
    </Row>

    <Modal v-model="collectionRoleManageModal" width="700" :title="$t('t_to_be_favorites')" :mask-closable="false">
      <Form :label-width="100">
        <FormItem :label="$t('t_name')">
          <Input v-model="collectionParams.name"></Input>
        </FormItem>
        <FormItem :label="$t('description')">
          <Input v-model="collectionParams.description"></Input>
        </FormItem>
        <FormItem :label="$t('t_regular_expression')">
          <FilterRules
            style="display:inline-block;vertical-align: middle;padding:0"
            class="col-md-12"
            :needAttr="true"
            v-model="collectionParams.expression"
            :allDataModelsWithAttrs="allEntityType"
          ></FilterRules>
        </FormItem>
      </Form>
      <div>
        <div class="role-transfer-title">{{ $t('mgmt_role') }}</div>
        <Transfer
          :titles="transferTitles"
          :list-style="transferStyle"
          :data="allRoles"
          :target-keys="MGMT"
          @on-change="handleMgmtRoleTransferChange"
          filterable
        ></Transfer>
      </div>
      <div style="margin-top: 30px">
        <div class="role-transfer-title">{{ $t('use_role') }}</div>
        <Transfer
          :titles="transferTitles"
          :list-style="transferStyle"
          :data="allRolesBackUp"
          :target-keys="USE"
          @on-change="handleUseRoleTransferChange"
          filterable
        ></Transfer>
      </div>
      <div slot="footer">
        <Button @click="collectionRoleManageModal = false">{{ $t('bc_cancel') }}</Button>
        <Button type="primary" @click="confirmCollection">{{ $t('bc_confirm') }}</Button>
      </div>
    </Modal>
  </div>
</template>
<script>
import {
  getHost,
  getRoleList,
  getRolesByCurrentUser,
  addCollection,
  getAllDataModels,
  getFavoritesList,
  getAssetsByExpression,
  deleteFavorites,
  editCollection
} from '@/api/server'
import FilterRules from './components/filter-rules.vue'
import Terminal from './terminal/terminal'
export default {
  name: '',
  data () {
    return {
      currentHostTab: 'default',
      selectedCollectionId: '',
      favoritesLists: [],
      expressionPath: '',
      showFilterRules: false,

      showHostList: true,
      showHideIcon: false, // 收起控制
      showDisplayIcon: false, // 展开控制
      // sendForAll: true,
      sendHostSet: [],
      searchHost: '',
      hostInfo: [], // 搜索后数据
      oriHostInfo: [], // 原始全量数据
      hostInfoToShow: [], // 搜索后分页显示数据

      activeTab: '',
      terminalTabs: [],
      sendForAll: false,

      uniteCmd: '',

      consoleConfig: {
        terminalH: '',
        rows: 0,
        cols: 0
      },
      showCmd: false,

      collectionRoleManageModal: false,
      collectionName: '',
      description: '',

      isAddCollect: false,
      allRoles: [],
      MGMT: [],
      allRolesBackUp: [],
      USE: [],
      transferTitles: [this.$t('unselected_role'), this.$t('selected_role')],
      transferStyle: { width: '300px' },
      collectionParams: {
        name: '',
        description: '',
        expression: '',
        roles: {
          owner: [],
          executor: []
        }
      },
      favoriteId: '',
      allEntityType: [],

      selectedCmd: '',
      isStartSelected: false,
      altDirect: 'up',
      selectedCmdIndex: -1,
      historyCmd: [],
      // 结果分页
      current: 1,
      pageSize: 20
    }
  },
  mounted () {
    this.initConsole()
    this.getHostList()
  },
  methods: {
    showRegular () {
      return !!window.request
    },
    warpCmd () {
      this.uniteCmd = this.uniteCmd + '\n'
    },
    sendCmd () {
      this.isStartSelected = false
      this.sendCmdValidate()
    },
    upCmd () {
      if (this.historyCmd.length === 0 || this.selectedCmdIndex === 0) return
      if (this.selectedCmdIndex === -1) {
        this.selectedCmdIndex = this.historyCmd.length - 1
      } else {
        this.selectedCmdIndex--
      }
      this.uniteCmd = this.historyCmd[this.selectedCmdIndex] && this.historyCmd[this.selectedCmdIndex].label + ''
    },
    downCmd () {
      if (this.selectedCmdIndex > -1 && this.selectedCmdIndex <= this.historyCmd.length - 1) {
        this.selectedCmdIndex++
        this.uniteCmd = this.historyCmd[this.selectedCmdIndex] && this.historyCmd[this.selectedCmdIndex].label + ''
      }
    },
    async changeHostTabs (name) {
      this.showFilterRules = false
      this.currentHostTab = name
      this.hostInfo = []
      this.oriHostInfo = []
      this.hostInfoToShow = []
      this.selectedCollectionId = ''
      this.searchHost = ''
      if (name === 'default') {
        this.getHostList()
      } else if (name === 'favorites') {
        // this.favoritesList()
      } else {
        this.expressionPath = ''
        this.showFilterRules = true
        await this.getAllDataModels()
      }
    },
    async changeCollections (val) {
      if (!val) return
      const item = this.favoritesLists.find(i => i.id === Number(val))
      const { status, data } = await getAssetsByExpression(item.expression)
      if (status === 'OK') {
        data.data.forEach(item => {
          item.showName = item.ip_address
          return item
        })
        this.hostInfo = data.data
        this.oriHostInfo = JSON.parse(JSON.stringify(this.hostInfo))
        this.current = 1
        this.finalData()
      }
    },
    clearSelectedCollectionId () {
      this.selectedCollectionId = ''
      this.hostInfo = []
      this.oriHostInfo = []
    },
    async favoritesList () {
      const { status, data } = await getFavoritesList()
      if (status === 'OK') {
        this.favoritesLists = data.data
      }
    },
    showDeleteConfirm (item) {
      this.$nextTick(() => {
        this.$Modal.confirm({
          title: this.$t('confirm_to_delete'),
          content: new Option(item.name).innerHTML,
          onOk: () => {
            this.deleteCollection(item)
          },
          onCancel: () => {}
        })
      })
    },
    async deleteCollection (item) {
      const { status, message } = await deleteFavorites(item.id)
      if (status === 'OK') {
        this.clearSelectedCollectionId()
        this.$Message.success(message)
      }
    },
    async getAllDataModels () {
      let { data, status } = await getAllDataModels()
      if (status === 'OK') {
        this.allEntityType = data
      }
    },
    async openCollectionModal (isAdd, params) {
      this.isAddCollect = isAdd
      if (isAdd) {
        this.MGMT = []
        this.USE = []
        this.collectionParams.name = this.collectionParams.description = ''
        this.collectionParams.expression = this.expressionPath
      } else {
        const { name, description, expression, roles, id } = params
        this.favoriteId = id
        this.collectionParams = {
          name,
          description,
          expression,
          roles: {
            owner: [],
            executor: []
          }
        }
        this.MGMT = roles.owner
        this.USE = roles.executor
      }
      await this.getRoleList()
      await this.getRolesByCurrentUser()
      await this.getAllDataModels()
      this.collectionRoleManageModal = true
    },
    async getAssetsByExpression () {
      const { status, data } = await getAssetsByExpression(this.expressionPath)
      if (status === 'OK') {
        data.data.forEach(item => {
          item.showName = item.ip_address
          return item
        })
        this.hostInfo = data.data
        this.oriHostInfo = JSON.parse(JSON.stringify(this.hostInfo))
        this.current = 1
        this.finalData()
      }
    },
    async getRoleList () {
      const { status, data } = await getRoleList()
      if (status === 'OK') {
        this.allRolesBackUp = data.map(_ => {
          return {
            ..._,
            key: _.name,
            label: _.displayName
          }
        })
      }
    },
    async getRolesByCurrentUser () {
      const { status, data } = await getRolesByCurrentUser()
      if (status === 'OK') {
        this.allRoles = data.map(_ => {
          return {
            ..._,
            key: _.name,
            label: _.displayName
          }
        })
      }
    },
    async handleMgmtRoleTransferChange (newTargetKeys, direction, moveKeys) {
      this.MGMT = newTargetKeys
    },
    async handleUseRoleTransferChange (newTargetKeys, direction, moveKeys) {
      this.USE = newTargetKeys
    },
    async confirmCollection () {
      if (!this.MGMT.length) {
        this.$Message.warning(this.$t('bc_mgmt_role_cannot_empty'))
        return
      }
      this.collectionParams.roles.owner = this.MGMT
      this.collectionParams.roles.executor = this.USE
      let result
      if (this.isAddCollect) {
        result = await addCollection([this.collectionParams])
      } else {
        result = await editCollection(this.favoriteId, this.collectionParams)
        this.clearSelectedCollectionId()
      }
      if (result.status === 'OK') {
        this.$Message.success(this.$t('tips.success'))
        this.collectionRoleManageModal = false
      }
    },
    mouseenter (type) {
      this[type] = true
    },
    mouseleave (type) {
      setTimeout(() => {
        this[type] = false
      }, 1000)
    },
    hideHost () {
      this.showHostList = false
      this.resizeConsole()
      this.showHideIcon = false
      this.showDisplayIcon = false
    },
    showHost () {
      this.showHostList = true
      this.resizeConsole()
      this.showHideIcon = false
      this.showDisplayIcon = false
    },
    cancelTerminalInteraction () {
      this.initConsole()
      this.showCmd = false
      const tab = this.terminalTabs.find(item => item.showName === this.activeTab)
      tab && this.focusConsole(tab.uniqueCode)
    },
    sendForMulti () {
      const height = document.body.scrollHeight
      this.consoleConfig.terminalH = height - 350
      let terminalH = (height - 256) / 17
      terminalH = Math.floor(terminalH)
      this.consoleConfig.rows = terminalH
      this.showCmd = true
    },
    resizeConsole () {
      const width = document.body.scrollWidth
      let terminalW
      if (this.showHostList) {
        terminalW = ((width - 260) * 18) / 24 / 8.2
      } else {
        terminalW = (width - 260) / 8.2
      }
      terminalW = Math.floor(terminalW)
      this.consoleConfig.cols = terminalW
      this.terminalTabs.forEach(item => {
        this.$nextTick(() => {
          this.$refs[item.uniqueCode][0].resizeScreen()
        })
      })
      const tab = this.terminalTabs.find(item => item.showName === this.activeTab)
      if (tab) {
        this.focusConsole(tab.uniqueCode)
      }
    },
    initConsole () {
      const height = document.body.scrollHeight
      this.consoleConfig.terminalH = height - 150
      let terminalH = (height - 210) / 17
      terminalH = Math.floor(terminalH)
      this.consoleConfig.rows = terminalH

      const width = document.body.scrollWidth
      let terminalW = ((width - 260) * 18) / 24 / 8.2
      terminalW = Math.floor(terminalW)
      this.consoleConfig.cols = terminalW
    },
    randomString (e) {
      e = e || 32
      const t = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
      const a = t.length
      let n = ''
      for (let i = 0; i < e; i++) n += t.charAt(Math.floor(Math.random() * a))
      return n
    },
    sendHistoryCmd () {
      this.uniteCmd = this.selectedCmd + '\n'
      this.sendCmdValidate()
    },
    sendCmdValidate () {
      if (!this.sendHostSet.length) {
        this.$Notice.warning({
          title: 'Warning',
          desc: this.$t('t_select_terminal')
        })
        return
      }
      const tmp = this.uniteCmd.replaceAll('\n', '@#%^&')
      const cacheCmd = tmp.substring(0, tmp.length - 5)
      const finalCmd = cacheCmd.replaceAll('@#%^&', '\n')
      this.historyCmd.push({ label: finalCmd, value: this.randomString() })
      this.sendHostSet.forEach(item => {
        this.$refs[item][0].externalTrigger(this.uniteCmd)
      })
      this.selectedCmdIndex = -1
      this.uniteCmd = ''
      this.selectedCmd = ''
    },
    switchCheck () {
      this.sendForAll = false
      if (this.sendHostSet.length === this.terminalTabs.length && this.terminalTabs.length !== 0) {
        this.sendForAll = true
      }
    },
    switchAllSelect (val) {
      this.sendHostSet = []
      this.sendForAll = false
      if (val) {
        this.sendForAll = true
        this.terminalTabs.forEach(item => {
          this.sendHostSet.push(item.uniqueCode)
        })
      }
    },
    filterHost () {
      this.current = 1
      this.finalData()
    },
    async getHostList () {
      const { status, data } = await getHost()
      if (status === 'OK') {
        data.data.forEach(item => {
          item.showName = item.ip_address
          return item
        })
        this.hostInfo = data.data
        this.oriHostInfo = JSON.parse(JSON.stringify(this.hostInfo))
        this.current = 1
        this.finalData()
      }
    },
    pageChange (page) {
      this.current = page
      this.finalData()
    },
    finalData () {
      const startNumber = (this.current - 1) * this.pageSize
      if (this.searchHost === '') {
        this.hostInfo = this.oriHostInfo
        this.hostInfoToShow = this.hostInfo.slice(startNumber, startNumber + this.pageSize)
      } else {
        this.hostInfo = this.oriHostInfo.filter(
          item => item.ip_address.includes(this.searchHost) || item.name.includes(this.searchHost)
        )
        this.hostInfoToShow = this.hostInfo.slice(startNumber, startNumber + this.pageSize)
      }
    },
    openTerminal (host) {
      this.switchAllSelect(false)
      // eslint-disable-next-line no-unused-vars
      let lastTab = ''
      this.terminalTabs.forEach(item => {
        if (item.label === host.ip_address) {
          lastTab = item
        }
      })
      let showName = ''
      if (!lastTab) {
        this.terminalTabs.push({
          index: 0,
          connnection_url: host.connnection_url,
          showName: host.showName,
          label: host.ip_address,
          key: host.id,
          uniqueCode: `${host.id}0`
        })
        showName = host.showName
      } else {
        const index = ++lastTab.index
        this.terminalTabs.push({
          index: index,
          connnection_url: host.connnection_url,
          showName: `${host.showName}(${index})`,
          label: host.ip_address,
          key: host.id,
          uniqueCode: `${host.id}${index}`
        })
        showName = `${host.showName}(${index})`
      }
      this.activeTab = showName || host.ip_address
    },
    handleTabRemove (name) {
      const tab = this.terminalTabs.find(item => item.showName === name)
      const uniqueCode = tab.uniqueCode
      const indexSet = this.sendHostSet.findIndex(item => item === uniqueCode)
      this.sendHostSet.splice(indexSet, 1)

      const index = this.terminalTabs.findIndex(item => item.showName === name)
      this.terminalTabs.splice(index, 1)
      if (this.terminalTabs.length > 0) {
        const lastTab = this.terminalTabs.slice(-1)[0]
        this.activeTab = lastTab.showName
        this.focusConsole(lastTab.uniqueCode)
      } else {
        this.cancelTerminalInteraction()
      }
    },
    clickTab (godTab) {
      const tab = this.terminalTabs.find(item => item.showName === godTab)
      this.activeTab = tab.showName
      this.focusConsole(tab.uniqueCode)
    },
    exectDangerousCmd () {
      this.sendHostSet.forEach(item => {
        this.$refs[item][0].confirmToExecution()
      })
    },
    cancelDangerousCmd () {
      this.sendHostSet.forEach(item => {
        this.$refs[item][0].cancelConfirmToExecution()
      })
    },
    focusConsole (uniqueCode) {
      this.$nextTick(() => {
        this.$refs[uniqueCode][0].focus()
      })
    }
  },
  components: {
    Terminal,
    FilterRules
  }
}
</script>
<style scoped lang="less">
.ivu-form-item {
  margin-bottom: 4px;
}
.hide-icon {
  cursor: pointer;
  width: 24px;
  color: #b2b4b8;
  position: absolute;
  z-index: 100;
  top: 10px;
}

.hide-icon-left {
  &:extend(.hide-icon);
  right: -2px;
}
.hide-icon-right {
  &:extend(.hide-icon);
  left: 2px;
}

.hide-icon-left:hover {
  color: #5ea7f3;
}
.hide-icon-right:hover {
  color: #5ea7f3;
}
</style>
<style scoped lang="less">
.diyTitle {
  width: calc(100% - 80px);
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  vertical-align: bottom;
}
.container-host {
  overflow-y: auto;
  height: ~'calc(100vh - 210px)';
}
.container-height {
  border: 1px solid #c4d3f1;
  height: ~'calc(100vh - 130px)';
  width: ~'calc(100% - 30px)';
}

.normal-icon {
  font-size: 18px;
  border-radius: 4px;
  width: 24px;
  margin-right: 6px;
}

.operation-icon-confirm:extend(.normal-icon) {
  border: 1px solid #57a3f3;
  color: #57a3f3;
  line-height: 24px;
}
.operation-icon-terminal:extend(.normal-icon) {
  padding-left: 2px;
  border: 1px solid black;
  color: black;
  line-height: 22px;
}

.host-content {
  margin: 2px 0;
}
.host-content-title {
  font-size: 16px;
  margin-right: 4px;
}
.role-transfer-title {
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  background-color: rgb(226, 222, 222);
  margin-bottom: 5px;
}
.search-input {
  width: ~'calc(100% - 90px)';
}
</style>
