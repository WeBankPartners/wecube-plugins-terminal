<template>
  <div>
    <Row>
      <Col span="5">
        <div>
          <Card>
            <h4 slot="title">
              {{$t('t_asset_id')}}
            </h4>
            <div class="container-host">
              <Input
                v-model="searchHost"
                placeholder="Enter something..."
                @on-change="filterHost"
                style="width: 100%;margin-bottom:16px"
              />
              <Collapse v-model="value1">
                <template v-for="host in hostInfo">
                  <Panel :name="host.ip_address" :key="host.ip_address">
                    <span>{{ host.ip_address }}</span>
                    <span style="color:#2d8cf0">[{{ host.username }}]</span>
                    <template>
                      <Tooltip content="Console" style="float:right">
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
                        <span class="host-content-title">ID:</span>
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
            </div>
          </Card>
        </div>
      </Col>
      <Col span="19">
        <div class="container-height">
          <Split v-model="split2" mode="vertical">
            <div slot="top">
              <Tabs type="card" closable :animated="false" @on-tab-remove="handleTabRemove" :value="activeTab">
                <template v-for="tab in terminalTabs">
                  <TabPane :label="tab.showName" :name="tab.showName" :key="tab.uniqueCode">
                    <Terminal :ref="tab.uniqueCode" :host="tab"></Terminal>
                  </TabPane>
                </template>
              </Tabs>
            </div>
            <div slot="bottom">
              <div style="margin:8px">
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
              </div>
              <Input
                v-model="uniteCmd"
                type="textarea"
                :autosize="{ minRows: 7, maxRows: 16 }"
                @on-enter="sendCmdValidate"
                placeholder="Enter something..."
              />
            </div>
          </Split>
        </div>
      </Col>
    </Row>
  </div>
</template>

<script>
import { getHost } from '@/api/server'
import Terminal from './terminal/terminal'
export default {
  name: '',
  data () {
    return {
      value1: '1',
      split2: 0.75,
      showHostList: true,
      // sendForAll: true,
      sendHostSet: [],
      searchHost: '',
      hostInfo: [],
      oriHostInfo: [],

      activeTab: '',
      terminalTabs: [],
      sendForAll: false,

      uniteCmd: ''
    }
  },
  computed: {},
  mounted () {
    this.getHostList()
  },
  methods: {
    sendCmdValidate () {
      if (!this.sendHostSet.length) {
        this.$Notice.warning({
          title: 'Warning',
          desc: '请选择终端机器'
        })
        return
      }
      this.sendHostSet.forEach(item => {
        this.$refs[item][0].externalTrigger(this.uniteCmd)
      })
      this.uniteCmd = ''
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
      if (this.searchHost) {
        this.hostInfo = this.oriHostInfo.filter(item => item.ip_address.includes(this.searchHost))
      } else {
        this.hostInfo = this.oriHostInfo
      }
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
      this.activeTab = showName
    },
    handleTabRemove (name) {
      const index = this.terminalTabs.findIndex(item => item.label === name)
      this.terminalTabs.splice(index, 1)
    }
  },
  components: {
    Terminal
  }
}
</script>

<style scoped lang="less">
.container-host {
  overflow-y: auto;
  height: ~'calc(100vh - 100px)';
}
.container-height {
  border: 1px solid #c4d3f1;
  height: ~'calc(100vh - 10px)';
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
</style>
