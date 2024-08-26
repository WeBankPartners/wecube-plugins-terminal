<template>
  <div class="">
    <Button @click="openTerminalFileMgmt" class="file-operate" type="primary">{{ $t('t_file_management') }}</Button>
    <div
      class="file-content"
      :style="{
        display: isOpenDrawer ? 'inherit' : 'none'
      }"
      type="primary"
    >
      <div style="margin-top: 8px">
        <Upload
          ref="uploadButton"
          show-upload-list
          :on-success="uploadSucess"
          :on-error="uploadFailed"
          :action="uploadUrl"
          :headers="headers"
          style="display:inline-block"
        >
          <Button icon="ios-cloud-upload-outline" :disabled="!filePermisson.includes('upload')">{{
            $t('t_file_upload')
          }}</Button>
        </Upload>

        <Button @click="closeDrawer" type="primary" style="position: absolute;right: 40px;">{{ $t('t_close') }}</Button>
      </div>
      <div style="margin: 4px 0">
        {{ $t('t_current_directory') }}：
        <Input style="width:60%" v-model="currentDir" @on-enter="getFiles"> </Input>
      </div>
      <div
        :style="{
          height: consoleConfig.terminalH - 145 + 'px',
          overflow: 'auto'
        }"
      >
        <template v-for="(file, index) in fileLists">
          <div :key="index">
            <label style="width:80px">{{ file.mode }} </label>
            <label style="width:50px">{{ file.gid }} </label>
            <label style="width:50px">{{ file.uid }} </label>
            <label style="width:100px" :title="file.size">{{ byteConvert(file.size) }}</label>
            <label style="width:100px">{{ file.mtime }} </label>
            <label class="file-name" @click="getFileList(file)">
              <Icon v-if="file.type === 'dir'" type="ios-folder" />
              <Icon v-if="file.type === 'link'" type="ios-link" />
              <Icon v-if="file.type === 'file'" type="md-document" />
              {{ file.name }}
            </label>
          </div>
        </template>
      </div>
    </div>
    <div id="terminal" ref="terminal"></div>
    <Modal v-model="confirmModal.isShowConfirmModal" width="900">
      <div>
        <Icon :size="28" :color="'#f90'" type="md-help-circle" />
        <span class="confirm-msg">{{ $t('confirm_to_exect') }}</span>
      </div>
      <div style="max-height: 400px;overflow-y: auto;">
        <pre style="margin-left: 44px;">{{ this.confirmModal.message }}</pre>
      </div>
      <div slot="footer">
        <span style="margin-left:30px;color:#ed4014;float: left;text-align:left">
          <Checkbox v-model="confirmModal.check">{{ $t('dangerous_confirm_tip') }}</Checkbox>
        </span>
        <Button type="text" @click="cancelConfirm">{{ $t('bc_cancel') }}</Button>
        <Button type="warning" :disabled="!confirmModal.check" @click="dangerousCmd">{{ $t('bc_confirm') }}</Button>
      </div>
    </Modal>
    <!-- 文件管理 -->
    <Drawer :title="$t('t_file_management')" width="730" :closable="false" v-model="terminalMgmtDrawer">
      <FileMgmt ref="fileMgmtRef" @closeDrawer="closeDrawer"></FileMgmt>
    </Drawer>
  </div>
</template>

<script>
import { getFileManagementPermission } from '@/api/server'
import { setCookie, getCookie } from '../util/cookie'
import { byteConvert } from '../util/functools'
import axios from 'axios'
import { Terminal } from 'xterm'
// import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import FileMgmt from './file-mgmt.vue'
export default {
  name: '',
  data () {
    return {
      shellWs: '',
      term: '', // 保存terminal实例
      // fitAddon: null,
      ssh_session: '',

      isOpenDrawer: false,
      filePermisson: [],
      fileLists: '',
      currentDir: '',
      headers: {},

      confirmModal: {
        isShowConfirmModal: false,
        check: false,
        message: ''
      },
      cmd: '', // 缓存命令
      terminalMgmtDrawer: false // 终端管理抽屉
    }
  },
  computed: {
    uploadUrl () {
      return `/terminal/v1/assets/${this.host.key}/file?path=` + encodeURIComponent(this.currentDir)
    }
  },
  props: ['host', 'consoleConfig', 'sendHostSet'],
  created () {},
  async mounted () {
    await this.initTerminal()
    await this.terminalConnect()
    this.operate()
    this.getHeaders()
  },
  methods: {
    // #region 文件管理
    openTerminalFileMgmt () {
      this.terminalMgmtDrawer = true
      this.$refs.fileMgmtRef.openDrawer(this.host, this.ssh_session)
    },
    closeDrawer () {
      this.terminalMgmtDrawer = false
      this.focus()
    },
    // #endregion
    focus () {
      this.term.focus()
    },
    byteConvert (size) {
      return byteConvert(size)
    },
    async initTerminal () {
      const term = new Terminal({
        rendererType: 'canvas', // 渲染类型
        rows: this.consoleConfig.rows, // 行数
        cols: this.consoleConfig.cols, // 不指定行数，自动回车后光标从下一行开始
        convertEol: true, // 启用时，光标将设置为下一行的开头
        scrollback: 500, // 终端中的回滚量
        disableStdin: false, // 是否应禁用输入。
        cursorStyle: 'underline', // 光标样式
        cursorBlink: true, // 光标闪烁
        theme: {
          foreground: '#7e9192', // 字体
          background: '#002833', // 背景色
          cursor: 'help', // 设置光标
          lineHeight: 16
        }
      })
      term.open(this.$refs['terminal'])
      // this.fitAddon = new FitAddon()
      // term.loadAddon(this.fitAddon)
      // this.fitAddon.fit()
      term.focus()
      this.term = term
    },
    resizeScreen () {
      // this.fitAddon.fit()
      this.term.resize(this.consoleConfig.cols, this.consoleConfig.rows)
      this.ssh_session &&
        this.ssh_session.send(
          JSON.stringify({ type: 'resize', data: { rows: this.consoleConfig.rows, cols: this.consoleConfig.cols } })
        )
    },
    async terminalConnect () {
      if (this.ssh_session) {
        // 如果已经连接了，就关闭，重新连接
        this.ssh_session.close()
      }
      var s = new WebSocket(this.host.connnection_url + '/terminal/v1/ssh')
      s.onopen = () => {
        s.send(
          JSON.stringify({
            type: 'init',
            data: {
              asset_id: this.host.key,
              token: getCookie('accessToken'),
              cols: this.consoleConfig.cols,
              rows: this.consoleConfig.rows
            }
          })
        )
      }
      s.onmessage = e => {
        let data = JSON.parse(e.data)
        if (data.type === 'console') {
          this.term.write(data.data) // (window.atob(data.data))
        } else if (data.type === 'listdir') {
          this.$refs.fileMgmtRef.showDir(data)
        } else if (data.type === 'warn') {
          this.confirm(data)
        } else if (data.type === 'error') {
          this.$Notice.error({
            title: 'Error',
            desc: data.data
          })
        }
      }
      // 把s挂到全局
      this.ssh_session = s
    },
    operate () {
      this.term.onData(data => {
        if (this.ssh_session.readyState === 1) {
          this.cmd = data
          this.ssh_session.send(JSON.stringify({ type: 'console', data: data }))
          // if (data == 'l'){
          //   this.ssh_session.send(JSON.stringify({type: "listdir", data: '.'}))
          // }
        } else {
          this.term.write('\r\nReConnecting...\r\n')
          this.terminalConnect()
        }
      })
    },
    externalTrigger (cmd) {
      this.cmd = cmd
      this.ssh_session.send(JSON.stringify({ type: 'console', data: cmd }))
    },
    getFiles () {
      this.ssh_session.send(JSON.stringify({ type: 'listdir', data: this.currentDir }))
    },
    async openDrawer () {
      const res = await getFileManagementPermission(this.host.key)
      this.filePermisson = res.data
      this.isOpenDrawer = true
      this.ssh_session.send(JSON.stringify({ type: 'listdir', data: '.' }))
    },
    showDir (listDir) {
      this.fileLists = listDir.data.filelist
      this.currentDir = listDir.data.pwd
      this.getHeaders()
    },
    getFileList (file) {
      if (['link', 'file'].includes(file.type)) {
        this.downLoadFile(file)
      } else if (file.type === 'dir') {
        this.ssh_session.send(JSON.stringify({ type: 'listdir', data: file.fullpath }))
      }
    },
    downLoadFile (file) {
      const api = `/terminal/v1/assets/${this.host.key}/file?path=`
      window.open(api + encodeURIComponent(file.fullpath), '_blank')
    },
    uploadSucess (response) {
      this.$refs.uploadButton.clearFiles()
      this.$Notice.info({
        title: response.status,
        desc: response.message
      })
      this.ssh_session.send(JSON.stringify({ type: 'listdir', data: this.currentDir }))
    },
    uploadFailed (msg) {
      console.log(msg)
      console.log('faild')
    },
    async getHeaders () {
      let refreshRequest = null
      const currentTime = new Date().getTime()
      const accessToken = getCookie('accessToken')
      if (accessToken) {
        const expiration = getCookie('accessTokenExpirationTime') * 1 - currentTime
        if (expiration < 1 * 60 * 1000 && !refreshRequest) {
          const isPlugin = window.request ? '/auth/v1/api/token' : '/terminal/v1/refresh-token'
          refreshRequest = axios.get(isPlugin, {
            headers: {
              Authorization: 'Bearer ' + getCookie('refreshToken')
            }
          })
          refreshRequest.then(
            res => {
              setCookie(res.data.data)
              this.setUploadActionHeader()
            },
            // eslint-disable-next-line handle-callback-err
            err => {
              refreshRequest = null
              window.location.href = window.location.origin + window.location.pathname + '#/login'
            }
          )
        } else {
          this.setUploadActionHeader()
        }
      } else {
        window.location.href = window.location.origin + window.location.pathname + '#/login'
      }
    },
    setUploadActionHeader () {
      this.headers = {
        Authorization: 'Bearer ' + getCookie('accessToken')
      }
    },
    confirm (data) {
      this.confirmModal.message = data.data
      this.confirmModal.check = false
      this.confirmModal.isShowConfirmModal = true
    },
    cancelConfirm () {
      this.confirmModal.isShowConfirmModal = false
      this.$emit('cancelDangerousCmd')
    },
    dangerousCmd () {
      if (this.sendHostSet.includes(this.host.uniqueCode)) {
        this.$emit('exectDangerousCmd')
      } else {
        this.confirmToExecution()
      }
    },
    async confirmToExecution () {
      this.confirmModal.isShowConfirmModal = false
      this.ssh_session.send(JSON.stringify({ type: 'console', confirm: true, data: this.cmd }))
      this.term.focus()
    },
    cancelConfirmToExecution () {
      this.confirmModal.isShowConfirmModal = false
    }
  },
  beforeDestroy () {
    this.ssh_session.close()
  },
  components: {
    FileMgmt
  }
}
</script>

<style scoped lang="less">
.file-operate {
  position: relative;
  z-index: 9;
  margin-top: 6px;
  right: 20px;
  float: right;
}
.file-content {
  position: absolute;
  z-index: 10;
  right: 0;
  background: #fefefef5;
  width: 730px;
  font-weight: 600;
  padding-left: 8px;
  color: #7e9192;
}
.file-name {
  word-break: break-all;
  width: 280px;
  vertical-align: top;
  cursor: pointer;
  color: #2d8cf0;
}
</style>
