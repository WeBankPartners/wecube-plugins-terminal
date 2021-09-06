<template>
  <div>
    <Header>
      <div class="menus">
        <Menu mode="horizontal" theme="dark">
          <Submenu v-for="menu in menus" :name="menu.code" :key="menu.code">
            <template>
              <template slot="title">
                {{ getTitle(menu) }}
              </template>
              <router-link v-for="submenu in menu.submenus" :key="submenu.code" :to="submenu.link || ''">
                <MenuItem v-if="submenu.isActive" :name="submenu.code" :disabled="!submenu.link">{{
                  getTitle(submenu)
                }}</MenuItem>
              </router-link>
            </template>
          </Submenu>
        </Menu>
      </div>
      <div class="header-right_container">
        <div class="profile">
          <Dropdown>
            <span style="color: white">{{ getUserName() }}</span>
            <Icon :size="18" type="md-arrow-dropdown"></Icon>
            <DropdownMenu slot="list">
              <DropdownItem name="logout">
                <a @click="logout" style="width: 100%; display: block">
                  {{ $t('logout') }}
                </a>
              </DropdownItem>
              <DropdownItem name="changePassword">
                <a @click="showChangePassword" style="width: 100%; display: block">
                  {{ $t('change_password') }}
                </a>
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>
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
    <Modal
      v-model="changePassword"
      :title="$t('change_password')"
      :mask-closable="false"
      @on-visible-change="cancelChangePassword"
    >
      <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="80">
        <FormItem :label="$t('old_password')" prop="oldPassword">
          <Input
            v-model="formValidate.oldPassword"
            type="password"
            :placeholder="$t('old_password_input_placeholder')"
          ></Input>
        </FormItem>
        <FormItem :label="$t('new_password')" prop="password">
          <Input
            v-model="formValidate.newPassword"
            type="password"
            :placeholder="$t('new_password_input_placeholder')"
          ></Input>
        </FormItem>
        <FormItem :label="$t('confirm_password')" prop="confirmPassword">
          <Input
            v-model="formValidate.confirmPassword"
            type="password"
            :placeholder="$t('confirm_password_input_placeholder')"
          ></Input>
        </FormItem>
      </Form>
      <div slot="footer">
        <Button @click="cancelChangePassword(false)">{{ $t('cancel') }}</Button>
        <Button type="primary" @click="okChangePassword">{{ $t('confirm') }}</Button>
      </div>
    </Modal>
  </div>
</template>
<script>
import Vue from 'vue'
import { changePassword, getUserMenus } from '@/api/server.js'
import { clearAllCookie } from '../util/cookie'
import { MENUS } from '@/const/menus.js'
export default {
  data () {
    return {
      user: '',
      currentLanguage: '',
      language: {
        'zh-CN': '简体中文',
        'en-US': 'English'
      },
      menus: [],
      changePassword: false,
      formValidate: {
        newPassword: '',
        oldPassword: '',
        confirmPassword: ''
      },
      ruleValidate: {
        newPassword: [{ required: true, message: 'New Password cannot be empty', trigger: 'blur' }],
        oldPassword: [{ required: true, message: 'Old Password cannot be empty', trigger: 'blur' }],
        confirmPassword: [{ required: true, message: 'Confirm Password cannot be empty', trigger: 'blur' }]
      }
    }
  },
  methods: {
    async getMenus () {
      this.menus = JSON.parse(JSON.stringify(MENUS))
      const { status, data } = await getUserMenus()
      if (status === 'OK') {
        data.forEach(_ => {
          let findSubmenus = this.menus.find(menu => menu.code === _.parent).submenus
          let findMenu = findSubmenus.find(m => m.code === _.id)
          findMenu.isActive = true
        })
      }
    },
    showChangePassword () {
      this.formValidate = {
        newPassword: '',
        oldPassword: '',
        confirmPassword: ''
      }
      this.changePassword = true
    },
    okChangePassword () {
      this.$refs['formValidate'].validate(async valid => {
        if (valid) {
          if (this.formValidate.newPassword === this.formValidate.confirmPassword) {
            const params = {
              // username: this.user,
              oldPassword: this.formValidate.oldPassword,
              newPassword: this.formValidate.newPassword
            }
            const { status } = await changePassword(params)
            if (status === 'OK') {
              this.$Message.success('Success !')
              this.changePassword = false
            }
          } else {
            this.$Message.warning(this.$t('confirm_password_error'))
          }
        }
      })
    },
    cancelChangePassword (flag = false) {
      if (!flag) {
        this.$refs['formValidate'].resetFields()
        this.changePassword = false
      }
    },
    getUserName () {
      this.user = localStorage.getItem('username')
      return this.user
    },
    logout () {
      localStorage.clear()
      clearAllCookie()
      window.location.href = window.location.origin + window.location.pathname + '#/login'
    },
    getTitle (menu) {
      const lang = localStorage.getItem('lang') || 'zh-CN'
      return lang === 'zh-CN' ? menu.cnName : menu.enName
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
  },
  mounted () {
    this.getMenus()
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
