<template>
  <Header>
    <div class="menus">
      <Menu mode="horizontal" theme="dark">
        <Submenu v-for="menu in menus" :name="menu.code" :key="menu.code">
          <template slot="title">
            {{ getTitle(menu) }}
          </template>
          <router-link v-for="submenu in menu.submenus" :key="submenu.code" :to="submenu.link || ''">
            <MenuItem :name="submenu.code" :disabled="!submenu.link">{{ getTitle(submenu) }}</MenuItem>
          </router-link>
        </Submenu>
      </Menu>
    </div>
    <div class="header-right_container">
      <div class="language">
        <Dropdown>
          <a href="javascript:void(0)">
            <Icon size="16" type="ios-globe" style="margin-right:5px; cursor: pointer" />
            {{ currentLanguage }}
            <Icon type="ios-arrow-down"></Icon>
          </a>
          <DropdownMenu slot="list">
            <DropdownItem v-for="(item, key) in language" :key="item.id" @click.native="changeLanguage(key)">{{
              item
            }}</DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>
    </div>
  </Header>
</template>
<script>
import Vue from 'vue'

export default {
  data () {
    return {
      user: '',
      currentLanguage: '',
      language: {
        'zh-CN': '简体中文',
        'en-US': 'English'
      },
      menus: [
        {
          code: 'system',
          cnName: '系统',
          enName: 'SYSTEM',
          seqNo: 1,
          parent: '',
          isActive: 'yes',
          submenus: [
            {
              code: 'terminal_asset',
              cnName: '终端管理',
              link: '/terminalManagement'
            },
            {
              code: 'terminal_authorization',
              cnName: '系统授权',
              link: ''
            },
            {
              code: 'terminal_permission',
              cnName: '终端授权',
              link: '/terminalAuthorization'
            }
          ]
        },
        {
          code: 'terminal',
          cnName: '终端',
          enName: 'TERMINAL',
          seqNo: 2,
          parent: '',
          isActive: 'yes',
          submenus: [
            {
              code: 'terminal_console',
              cnName: '终端连接',
              link: '/terminalOperation'
            }
          ]
        }
      ]
    }
  },
  methods: {
    getTitle (menu) {
      return localStorage.getItem('lang') === 'zh-CN' ? menu.cnName : menu.enName
    },
    changeLanguage (key) {
      Vue.config.lang = key
      this.currentLanguage = this.language[key]
      localStorage.setItem('lang', key)
    },
    getLocalLang () {
      let currentLangKey = localStorage.getItem('lang') || navigator.language || navigator.userLanguage
      currentLangKey = currentLangKey === 'zh-CN' ? currentLangKey : 'en-US'
      this.currentLanguage = this.language[currentLangKey]
    }
  },
  async created () {
    this.getLocalLang()
  },
  watch: {
    $lang: function (lang) {
      window.location.reload()
    }
  }
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  justify-content: center;

  .header-title {
    font-size: 16px;
    color: #fff;
    font-weight: 600;
    float: left;
    margin-right: 10px;
  }

  .ivu-layout-header {
    height: 50px;
    line-height: 50px;
    padding: 0 17px;
  }
  a {
    color: white;
  }

  .menus {
    display: inline-block;
    .ivu-menu-horizontal {
      height: 50px;
      line-height: 50px;

      .ivu-menu-submenu {
        padding: 0 10px;
      }
    }
  }

  .header-right_container {
    float: right;

    .language,
    .profile {
      float: right;
      display: inline-block;
      vertical-align: middle;
      margin-left: 20px;
    }
  }
}
</style>
