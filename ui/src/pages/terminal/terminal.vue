<template>
  <div class="">
    <Button @click="openDrawer" class="file-operate" type="primary">{{ $t('t_file_management') }}</Button>
    <div
      class="file-content"
      :style="{ height: consoleConfig.terminalH + 'px', display: isOpenDrawer ? 'inherit' : 'none', overflow: 'auto' }"
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
          <Button icon="ios-cloud-upload-outline" :disabled="!filePermisson.includes('download')">{{
            $t('t_file_upload')
          }}</Button>
        </Upload>

        <Button @click="isOpenDrawer = !isOpenDrawer" type="primary" style="position: absolute;right: 40px;">{{
          $t('t_close')
        }}</Button>
      </div>
      <span>{{ $t('t_current_directory') }}：</span> {{ currentDir }}
      <template v-for="(file, index) in fileLists">
        <div :key="index" style="">
          <label style="width:80px">{{ file.mode }} </label>
          <label style="width:50px">{{ file.gid }} </label>
          <label style="width:50px">{{ file.uid }} </label>
          <label style="width:100px">{{ file.size }} </label>
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
        <Button type="text" @click="confirmModal.isShowConfirmModal = false">{{ $t('bc_cancel') }}</Button>
        <Button type="warning" :disabled="!confirmModal.check" @click="confirmToExecution">{{
          $t('bc_confirm')
        }}</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { getFileManagementPermission } from '@/api/server'
import { setCookie, getCookie } from '../util/cookie'
import axios from 'axios'
import { Terminal } from 'xterm'
import 'xterm/css/xterm.css'
export default {
  name: '',
  data () {
    return {
      shellWs: '',
      term: '', // 保存terminal实例
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
      cmd: '' // 缓存命令
    }
  },
  computed: {
    uploadUrl () {
      return `/terminal/v1/assets/${this.host.key}/file?path=${this.currentDir}`
    }
  },
  props: ['host', 'consoleConfig'],
  created () {},
  async mounted () {
    await this.initTerminal()
    await this.terminalConnect()
    this.operate()
    this.getHeaders()
  },
  methods: {
    async initTerminal () {
      this.term = new Terminal({
        rendererType: 'canvas', // 渲染类型
        rows: this.consoleConfig.rows, // 行数
        cols: this.consoleConfig.cols, // 不指定行数，自动回车后光标从下一行开始
        convertEol: true, // 启用时，光标将设置为下一行的开头
        scrollback: 50, // 终端中的回滚量
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
      this.term.open(this.$refs['terminal'])
      this.term.focus()
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
          this.showDir(data)
        } else if (data.type === 'warn') {
          this.confirm(data)
        } else if (data.type === 'error') {
          this.$Notice.error({
            title: 'Error',
            desc: data.data
          })
        }
      }
      s.onclose = function (e) {
        this.term.write('\r\nConnection close')
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
      this.ssh_session.send(JSON.stringify({ type: 'console', data: cmd }))
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
        this.downFile(file)
      } else if (file.type === 'dir') {
        this.ssh_session.send(JSON.stringify({ type: 'listdir', data: file.fullpath }))
      }
    },
    downFile (file) {
      const api = `/terminal/v1/assets/${this.host.key}/file?path=${file.fullpath}`
      axios({
        method: 'GET',
        url: api,
        headers: this.headers,
        responseType: 'blob'
      })
        .then(async response => {
          if (response.data.type === 'application/json') {
            const errorMsg = JSON.parse(await response.data.text())
            this.$Notice.error({
              title: 'Error',
              desc: errorMsg.message
            })
            return
          }
          // eslint-disable-next-line no-unused-vars
          let fileStream = response.data
          let fileName = file.name
          let blob = new Blob([fileStream])
          if ('msSaveOrOpenBlob' in navigator) {
            // Microsoft Edge and Microsoft Internet Explorer 10-11
            window.navigator.msSaveOrOpenBlob(blob, fileName)
          } else {
            if ('download' in document.createElement('a')) {
              // 非IE下载
              let elink = document.createElement('a')
              elink.download = fileName
              elink.style.display = 'none'
              elink.href = URL.createObjectURL(blob)
              document.body.appendChild(elink)
              elink.click()
              URL.revokeObjectURL(elink.href) // 释放URL 对象
              document.body.removeChild(elink)
            } else {
              // IE10+下载
              navigator.msSaveOrOpenBlob(blob, fileName)
            }
          }
        })
        .catch(() => {
          this.$Notice.error({
            title: 'Error',
            desc: 'Download Faild'
          })
        })
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
          refreshRequest = axios.get('/auth/v1/api/token', {
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
      this.confirmModal.isShowConfirmModal = true
    },
    async confirmToExecution () {
      this.confirmModal.isShowConfirmModal = false
      this.ssh_session.send(JSON.stringify({ type: 'console', confirm: true, data: this.cmd }))
    }
  },
  components: {}
}
</script>

<style scoped lang="less">
.file-operate {
  position: absolute;
  z-index: 10;
  right: 40px;
}
.file-content {
  position: absolute;
  z-index: 10;
  right: 0;
  background: #fefefef5;
  width: 710px;
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
