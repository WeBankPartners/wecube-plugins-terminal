<template>
  <div class="">
    <Button @click="openDrawer" class="file-operate" type="primary">{{ $t('t_file_management') }}</Button>
    <div
      class="file-content"
      :style="{ height: this.terminalH, display: isOpenDrawer ? 'inherit' : 'none', overflow: 'auto' }"
      type="primary"
    >
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
      <Upload
        ref="uploadButton"
        show-upload-list
        :on-success="uploadSucess"
        :on-error="uploadFailed"
        :action="uploadUrl"
        :headers="headers"
        style="position: absolute;bottom: 0;"
      >
        <Button icon="ios-cloud-upload-outline">{{ $t('t_file_upload') }}</Button>
      </Upload>
      <Button
        @click="isOpenDrawer = !isOpenDrawer"
        style="margin-right: 10px;position: absolute;right: 0;bottom: 10px;"
        type="primary"
        >{{ $t('t_close') }}</Button
      >
    </div>
    <div id="terminal" ref="terminal"></div>
  </div>
</template>

<script>
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
      rows: 0,
      cols: 0,

      isOpenDrawer: false,
      fileLists: '',
      currentDir: '',
      headers: {},
      terminalH: ''
    }
  },
  computed: {
    uploadUrl () {
      return `/terminal/v1/assets/${this.host.key}/file?path=${this.currentDir}`
    }
  },
  props: ['host'],
  created () {},
  async mounted () {
    const height = document.body.scrollHeight
    this.terminalH = height * 0.75 - 68 + 'px'
    let terminalH = (height * 0.75 - 48) / 17
    terminalH = Math.floor(terminalH)
    this.rows = terminalH

    const width = document.body.scrollWidth
    let terminalW = ((width - 60) * 19) / 24 / 8.2
    terminalW = Math.floor(terminalW)
    this.cols = terminalW

    await this.initTerminal()
    await this.terminalConnect()
    this.operate()
    this.getHeaders()
  },
  methods: {
    async initTerminal () {
      this.term = new Terminal({
        rendererType: 'canvas', // 渲染类型
        rows: this.rows, // 行数
        cols: this.cols, // 不指定行数，自动回车后光标从下一行开始
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
              cols: this.cols,
              rows: this.rows
            }
          })
        )
      }
      s.onmessage = e => {
        let data = JSON.parse(e.data)
        if (data.type === 'console') {
          this.term.write(data.data) // (window.atob(data.data))
        } else if (data.type === 'listdir') {
          console.log('receive file list:', data)
          this.showDir(data)
        } else if (data.type === 'warn') {
          // show_confirm(data.data)
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
          // console.log('sending console:', JSON.stringify({ type: 'console', data: data }))
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

    openDrawer () {
      this.isOpenDrawer = true
      this.ssh_session.send(JSON.stringify({ type: 'listdir', data: '.' }))
    },
    showDir (listDir) {
      this.fileLists = listDir.data.filelist
      this.currentDir = listDir.data.pwd
      this.getHeaders()
    },
    getFileList (file) {
      if (file.type !== 'dir') {
        this.downFile(file)
      } else {
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
        .then(response => {
          // eslint-disable-next-line no-unused-vars
          let fileStream = response.data
          if (response.status < 400) {
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
    }
  },
  components: {}
}
</script>

<style scoped lang="less">
.file-operate {
  position: absolute;
  z-index: 10;
  right: 0;
}
.file-content {
  position: absolute;
  z-index: 10;
  right: 0;
  background: #fefefef5;
  width: 800px;
  font-weight: 600;
  padding-left: 8px;
  color: #7e9192;
}
.file-name {
  word-break: break-all;
  width: 280px;
  vertical-align: top;
}
</style>
