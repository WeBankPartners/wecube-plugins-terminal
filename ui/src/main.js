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
import locale from 'view-design/dist/locale/en-US'
import VueI18n from 'vue-i18n'
import './locale/i18n'
import './styles/index.less'

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
  locale
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
