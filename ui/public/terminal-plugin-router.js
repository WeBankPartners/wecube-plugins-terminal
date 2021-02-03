import router from '../src/router-plugin'
const implicitRoute = {
  'terminalManagement/sessionRecords': {
    parentBreadcrumb: { 'zh-CN': '终端管理', 'en-US': 'Terminal Config' },
    childBreadcrumb: { 'zh-CN': '会话记录', 'en-US': 'Session Records' }
  },
  'terminalManagement/transferRecords': {
    parentBreadcrumb: { 'zh-CN': '终端管理', 'en-US': 'Terminal Config' },
    childBreadcrumb: { 'zh-CN': '文件传输', 'en-US': 'Transfer Records' }
  },
  'terminalManagement/permissions': {
    parentBreadcrumb: { 'zh-CN': '终端管理', 'en-US': 'Terminal Config' },
    childBreadcrumb: { 'zh-CN': '权限管理', 'en-US': 'Permissions' }
  }
}

window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'terminal')
