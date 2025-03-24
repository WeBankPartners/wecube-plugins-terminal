<template>
  <div>
    <Row>
      <Col span="6" v-if="showHostList">
        <div class="hide-icon-left">
          <Icon type="ios-arrow-dropleft" color="#5384FF" @click="hideHost" size="20" />
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
                          <span v-if="item.is_owner" style="float: right">
                            <Button
                              icon="ios-trash"
                              type="error"
                              size="small"
                              @click="showDeleteConfirm(item)"
                            ></Button>
                          </span>
                          <span v-if="item.is_owner" style="float: right; margin-right: 10px">
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
                      style="display: inline-block; vertical-align: middle; padding: 0"
                      class="col-md-12"
                      :needAttr="true"
                      v-model="expressionPath"
                      :allDataModelsWithAttrs="allEntityType"
                    ></FilterRules>
                  </span>

                  <div style="display: flex; justify-content: space-around; margin: 12px">
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
              <div style="margin-bottom: 8px">
                <Input
                  v-model="searchHost"
                  :placeholder="$t('t_search_host')"
                  @on-enter="filterHost"
                  class="search-input"
                />
                <Button type="primary" @click="filterHost" style="width: 70px">{{ $t('button.search') }}</Button>
              </div>
              <template v-if="hostInfo.length > 0">
                <Collapse>
                  <template v-for="host in hostInfoToShow">
                    <Panel :name="host.ip_address" :key="host.ip_address">
                      <div class="diyTitle">
                        {{ host.ip_address }}<span style="color: #5384ff">[{{ host.username }}]</span>{{ host.name }}
                      </div>
                      <template>
                        <Tooltip content="Console" :delay="500" style="float: right">
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
                          <span style="word-break: break-all">{{ host.display_name }}</span>
                        </div>
                      </div>
                    </Panel>
                  </template>
                </Collapse>
                <!-- v-if="currentHostTab==='favorites'&&hostInfoToShow.length>0" -->
                <div style="margin-top: 6px; display: flex; justify-content: space-between">
                  <span>{{ $t('total') }}{{ hostInfo.length }}{{ $t('items') }}</span>
                  <Page
                    style="display: inline-block; vertical-align: bottom"
                    :page-size="pageSize"
                    :current="current"
                    @on-change="pageChange"
                    :total="hostInfo.length"
                    simple
                  />
                  <span>{{ pageSize }}{{ $t('page') }}</span>
                </div>

                <Button @click="startAll" style="float: right" type="success" size="small">{{
                  $t('t_start_all')
                }}</Button>
              </template>
              <template v-else>
                <div style="text-align: center; color: #969696; font-size: 12px">
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
          style="width: 20px; background: #fafafa; display: inline-block; height: calc(100vh - 130px)"
        >
          <div class="hide-icon-right">
            <Icon @click="showHost" color="#5384FF" type="ios-arrow-dropright" size="20" />
          </div>
        </div>
        <div
          class="container-height"
          :class="showHostList ? 'container-width-18' : 'container-width-24'"
          style="display: inline-block; vertical-align: top"
        >
          <div>
            <Tabs
              type="card"
              class="terminal-tabs"
              closable
              :animated="false"
              @on-click="clickTab"
              @on-tab-remove="handleTabRemove"
              :before-remove="beforeRemove"
              :value="activeTab"
            >
              <template v-for="tab in terminalTabs">
                <TabPane
                  :label="tab.showName"
                  :name="tab.showName"
                  :key="tab.uniqueCode"
                  class="terminal-tab"
                  style="visibility: visible"
                >
                  <!-- :style="{ 'overflow-y': 'auto' }" -->
                  <div>
                    <Terminal
                      :ref="tab.uniqueCode"
                      :host="tab"
                      :sendHostSet="sendHostSet"
                      :consoleConfig="consoleConfig"
                      :isSplitScreenMode="isSplitScreenMode"
                      @exectDangerousCmd="exectDangerousCmd"
                      @cancelDangerousCmd="cancelDangerousCmd"
                      @handleTabRemove="handleTabRemove"
                    ></Terminal>
                    <Button style="margin: 1px" v-if="!showCmd && !isSplitScreenMode" @click="sendForMulti">{{
                      $t('t_terminal_interaction')
                    }}</Button>
                  </div>
                </TabPane>
              </template>
              <div slot="extra" style="margin: 0 16px">
                <span style="vertical-align: sub">{{ $t('t_split_screen') }}</span>
                <i-switch
                  v-model="isSplitScreenMode"
                  @on-change="change"
                  true-color="#13ce66"
                  :disabled="terminalTabs.length <= 1"
                  style="vertical-align: bottom"
                />
              </div>
            </Tabs>
            <Button v-if="!showCmd && isSplitScreenMode" @click="sendForMulti">{{
              $t('t_terminal_interaction')
            }}</Button>
          </div>
          <div v-if="showCmd" class="interaction-region">
            <div style="margin: 1px">
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
              <Checkbox :value="sendForAll" @on-change="switchAllSelect" style="font-weight: 600"> ALL </Checkbox>
              <CheckboxGroup v-model="sendHostSet" @on-change="switchCheck" style="display: inline-block">
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
                style="float: right; margin: 0 16px"
                >{{ $t('t_send') }}</Button
              >
              <Select v-model="selectedCmd" style="float: right; width: 200px" placeholder="history cmd">
                <Option v-for="item in historyCmd" :value="item.label" :key="item.value">{{ item.label }}</Option>
              </Select>
            </div>
            <Input
              v-model="uniteCmd"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 3 }"
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
            style="display: inline-block; vertical-align: middle; padding: 0"
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
  addCollection,
  deleteFavorites,
  editCollection,
  getAllDataModels,
  getAssetsByExpression,
  getFavoritesList,
  getHost,
  getRoleList,
  getRolesByCurrentUser
} from '@/api/server'
import FilterRules from '@/pages/components/filter-rules.vue'
import Terminal from '@/pages/terminal/terminal'
const maxConnectionLimit = 21
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
      pageSize: 20,
      isSplitScreenMode: false // 是否开启分屏模式
    }
  },
  mounted () {
    this.initConsole()
    this.getHostList()
  },
  methods: {
    change (val) {
      this.startSplit(val)
    },
    startSplit (needChangeSplit) {
      this.isSplitScreenMode = needChangeSplit
      // 入口触发时，切换分屏，
      // 新打开终端时， 不切换状态，只计算尺寸
      // if (needChangeSplit) {
      //   this.isSplitScreenMode = !this.isSplitScreenMode
      // }
      // 获取所有tab内容
      const tabs = document.getElementsByClassName('terminal-tab')
      if (this.isSplitScreenMode) {
        // 分屏，并改变其尺寸、布局
        for (let i = 0; i < tabs.length; i++) {
          tabs[i].style.setProperty('visibility', 'visible', 'important')
          tabs[i].style.setProperty('display', 'inline-block', 'important')
          tabs[i].style.setProperty('width', '50%', 'important')
        }
        this.calculateConsoleSizeForSplit()
      } else {
        // 全屏，并改变其尺寸、布局
        for (let i = 0; i < tabs.length; i++) {
          tabs[i].style.setProperty('width', '100%', 'important')
          this.activeTab = this.terminalTabs[i].showName
          if (i === tabs.length - 1) {
            tabs[i].style.setProperty('visibility', 'visible', 'important')
          } else {
            tabs[i].style.setProperty('visibility', 'hidden', 'important')
            tabs[i].style.setProperty('display', 'none', 'important')
          }
        }
        this.calculateConsoleSizeForFull()
      }
      // 控制tab头是否显示
      const tabCard = document.querySelector('.terminal-tabs .ivu-tabs-nav-scroll')
      tabCard.style.setProperty('display', this.isSplitScreenMode ? 'none' : '', 'important')
    },
    // 分屏计算新窗口尺寸
    calculateConsoleSizeForSplit () {
      // const height = document.body.scrollHeight
      // let terminalH = (height - 260) / 8.2
      // terminalH = Math.floor(terminalH / 4)
      // console.log(1.8, terminalH)
      this.consoleConfig.rows = 22
      this.consoleConfig.cols = 70
      this.terminalTabs.forEach(item => {
        this.$nextTick(() => {
          this.$refs[item.uniqueCode][0].resizeScreen()
        })
      })
    },
    // 全屏计算新窗口尺寸
    calculateConsoleSizeForFull () {
      this.initConsole()
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
      this.startSplit(this.isSplitScreenMode)
    },
    showHost () {
      this.showHostList = true
      this.resizeConsole()
      this.showHideIcon = false
      this.showDisplayIcon = false
      this.startSplit(this.isSplitScreenMode)
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
      this.calculateRegion()
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
      this.consoleConfig.rows = terminalH - 5

      const width = document.body.scrollWidth
      let terminalW = ((width - 250) * 18) / 24 / 8.2
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
    startAll () {
      if (this.hostInfoToShow.length + this.terminalTabs.length >= maxConnectionLimit) {
        this.$Message.warning(this.$t('t_maximum_reached'))
        return
      }
      this.$Modal.confirm({
        title: this.$t('t_start_all_tip'),
        content: '',
        render: h => {
          const ipList = this.hostInfoToShow.map(item => {
            return h('Tag', item.ip_address)
          })
          return ipList
        },
        'z-index': 1000000,
        onOk: () => {
          this.hostInfoToShow.forEach(host => {
            this.openTerminal(host)
          })
        },
        onCancel: () => {}
      })
    },
    openTerminal (host) {
      if (this.terminalTabs.length >= maxConnectionLimit) {
        this.$Message.warning(this.$t('t_maximum_reached'))
        return
      }
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
      this.$nextTick(() => {
        this.startSplit(this.isSplitScreenMode)
      })
      this.activeTab = showName || host.ip_address
    },
    beforeRemove (tabIndex) {
      return new Promise(resolve => {
        this.$Modal.confirm({
          title: this.$t('t_close_terminal'),
          content: this.$t('t_close_terminal_tip') + this.terminalTabs[tabIndex].showName,
          'z-index': 1000000,
          onOk: () => {
            resolve() // 允许关闭
          },
          onCancel: () => {}
        })
      })
    },
    handleTabRemove (name) {
      const tab = this.terminalTabs.find(item => item.showName === name)
      const uniqueCode = tab.uniqueCode
      const indexSet = this.sendHostSet.findIndex(item => item === uniqueCode)
      this.sendHostSet.splice(indexSet, 1)

      const index = this.terminalTabs.findIndex(item => item.showName === name)
      this.terminalTabs.splice(index, 1)
      // 在terminalTabs数量小于1时，关闭分屏模式
      if (this.terminalTabs.length > 0) {
        if (this.terminalTabs.length === 1) {
          this.isSplitScreenMode = false
        }
        const lastTab = this.terminalTabs.slice(-1)[0]
        this.activeTab = lastTab.showName
        this.focusConsole(lastTab.uniqueCode)
      } else {
        this.isSplitScreenMode = false
        this.activeTab = ''
        this.cancelTerminalInteraction()
      }
      this.$nextTick(() => {
        this.startSplit(this.isSplitScreenMode)
      })
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
    },
    calculateRegion () {
      this.$nextTick(() => {
        const container = document.querySelector('.container-height')
        const terminal = document.querySelector('.terminal-tabs')
        const region = document.querySelector('.interaction-region')
        if (container && terminal && region) {
          const containerHeight = container.offsetHeight
          const terminalHeight = terminal.offsetHeight
          const cHeight = containerHeight - terminalHeight - 2
          region.style.height = `${cHeight}px`
        }
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
.interaction-region {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.terminal-tabs /deep/ .ivu-tabs-bar {
  margin-bottom: 0 !important;
}
</style>
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
  overflow: auto;
}

.container-width-18 {
  width: ~'calc(100% - 6px)';
}
.container-width-24 {
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
