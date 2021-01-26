import 'regenerator-runtime/runtime'
import router from './router-plugin'
import 'view-design/dist/styles/iview.css'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import jquery from 'jquery'
import zhCN from '@/locale/i18n/zh-CN.json'
import enUS from '@/locale/i18n/en-US.json'

import TerminalPageTable from '@/pages/components/table-page/page'
import ModalComponent from '@/pages/components/modal'

window.addOptions({
  JQ: jquery,
  $TerminalCommonUtil: commonUtil,
  $validate: validate
})

window.component('TerminalPageTable', TerminalPageTable)
window.component('ModalComponent', ModalComponent)

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'dangerous')