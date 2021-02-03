const router = [
  {
    path: '/terminalOperation',
    name: 'terminalOperation',
    redirect: 'terminalOperation',
    children: [
      {
        path: '/terminalOperation',
        name: 'terminalOperation',
        params: {},
        props: true
      }
    ]
  },
  {
    path: '/terminalManagement',
    name: 'terminalManagement',
    redirect: '/terminalManagement/sessionRecords',
    children: [
      {
        path: 'permissions',
        name: 'permissions',
        title: '文件传输权限',
        meta: {}
      },
      {
        path: 'sessionRecords',
        name: 'sessionRecords',
        title: '访问记录',
        meta: {}
      },
      {
        path: 'transferRecords',
        name: 'transferRecords',
        title: '文件传输列表',
        meta: {}
      }
    ]
  }
]

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
