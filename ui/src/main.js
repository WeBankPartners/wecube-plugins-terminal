import 'regenerator-runtime/runtime'
import ViewUI from 'view-design'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
// import 'view-design/dist/styles/iview.css'
import '@/assets/css/local.bootstrap.css'
import { validate } from '@/assets/js/validate.js'
import VeeValidate from '@/assets/veeValidate/VeeValidate'
import { commonUtil } from '@/pages/util/common-util.js'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import jquery from 'jquery'
import viewDesignEn from 'view-design/dist/locale/en-US'
import viewDesignZh from 'view-design/dist/locale/zh-CN'
import VueI18n from 'vue-i18n'
import './styles/index.less'
import { i18n } from './locale/i18n/index.js'

import ModalComponent from '@/pages/components/modal'
import TerminalPageTable from '@/pages/components/table-page/page'

Vue.use(VeeValidate)
Vue.prototype.$validate = validate
Vue.prototype.$TerminalCommonUtil = commonUtil
Vue.prototype.JQ = jquery
Vue.component('TerminalPageTable', TerminalPageTable)
Vue.component('ModalComponent', ModalComponent)

Vue.config.productionTip = false

Vue.use(ViewUI, {
  transfer: true,
  size: 'default',
  VueI18n,
  locale: i18n.locale === 'en-US' ? viewDesignEn : viewDesignZh
})

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#app')
