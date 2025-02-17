<template>
  <div class="">
    <div style="margin-top: 8px">
      <Upload
        ref="uploadButton"
        show-upload-list
        :on-success="uploadSucess"
        :on-error="uploadFailed"
        :action="uploadUrl"
        :headers="headers"
        style="display: inline-block"
      >
        <Button class="btn-upload" :disabled="!filePermisson.includes('upload')">
          <img src="@/styles/icon/UploadOutlined.png" class="upload-icon" />
          {{ $t('t_file_upload') }}
        </Button>
        <!-- <Button icon="ios-cloud-upload-outline" :disabled="!filePermisson.includes('upload')">{{
          $t('t_file_upload')
        }}</Button> -->
      </Upload>
    </div>
    <div style="margin: 4px 0">
      {{ $t('t_current_directory') }}：
      <Input style="width: 60%" v-model="currentDir" @on-enter="getFiles"> </Input>
    </div>
    <div class="file-list-content">
      <template v-for="(file, index) in fileLists">
        <div :key="index">
          <label style="width: 80px">{{ file.mode }} </label>
          <label style="width: 50px">{{ file.gid }} </label>
          <label style="width: 50px">{{ file.uid }} </label>
          <label style="width: 100px" :title="file.size">{{ byteConvert(file.size) }}</label>
          <label style="width: 100px">{{ file.mtime }} </label>
          <label class="file-name" @click="getFileList(file)">
            <Icon v-if="file.type === 'dir'" type="ios-folder" />
            <Icon v-if="file.type === 'link'" type="ios-link" />
            <Icon v-if="file.type === 'file'" type="md-document" />
            {{ file.name }}
          </label>
        </div>
      </template>
    </div>
    <div class="demo-drawer-footer">
      <Button type="primary" @click="closeDrawer">{{ $t('t_close') }}</Button>
    </div>
  </div>
</template>

<script>
import { getFileManagementPermission } from '@/api/server'
import { getCookie, setCookie } from '@/pages/util/cookie'
import { byteConvert } from '@/pages/util/functools'
import axios from 'axios'
// import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
export default {
  name: '',
  data () {
    return {
      term: '', // 保存terminal实例
      // fitAddon: null,
      ssh_session: '',
      filePermisson: [],
      fileLists: '',
      currentDir: '',
      headers: {},

      host: {} // 当前终端实例
    }
  },
  computed: {
    uploadUrl () {
      return `/terminal/v1/assets/${this.host.key}/file?path=` + encodeURIComponent(this.currentDir)
    }
  },
  created () {},
  async mounted () {
    this.getHeaders()
  },
  methods: {
    // #region 文件管理
    // #endregion
    getFiles () {
      this.ssh_session.send(JSON.stringify({ type: 'listdir', data: this.currentDir }))
    },
    async openDrawer (host, ssh_session) {
      this.host = host
      this.ssh_session = ssh_session
      const res = await getFileManagementPermission(this.host.key)
      this.filePermisson = res.data
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
      console.log(msg, 'faild')
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
    byteConvert (size) {
      return byteConvert(size)
    },
    closeDrawer () {
      this.$emit('closeDrawer')
    }
  }
}
</script>

<style scoped lang="less">
.file-list-content {
  height: ~'calc(100vh - 230px)';
  overflow: auto;
}
.demo-drawer-footer {
  width: 100%;
  position: absolute;
  bottom: 0;
  left: 0;
  border-top: 1px solid #e8e8e8;
  padding: 10px 16px;
  text-align: right;
  background: #fff;
}

.file-name {
  word-break: break-all;
  width: 280px;
  vertical-align: top;
  cursor: pointer;
  color: #5384ff;
}
</style>
