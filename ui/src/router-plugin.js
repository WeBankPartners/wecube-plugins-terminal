import terminalOperation from '@/pages/terminal-operation'
import terminalManagement from '@/pages/terminal-management'
import permissions from '@/pages/authorization/permissions'
import sessionRecords from '@/pages/authorization/session-records'
import transferRecords from '@/pages/authorization/transfer-records'
import terminalAuthorization from '@/pages/terminal-authorization'
import hosts from '@/pages/management/hosts'
import jumpServer from '@/pages/management/jump-server'

const router = [
  {
    path: '/terminal/terminalOperation',
    name: '/terminal/terminalOperation',
    component: terminalOperation,
    params: {},
    props: true
  },
  {
    path: '/terminal/terminalAuthorization',
    name: 'terminalAuthorization',
    redirect: '/terminal/terminalAuthorization/sessionRecords',
    component: terminalAuthorization,
    children: [
      {
        path: '/terminal/terminalAuthorization/permissions',
        name: 'permissions',
        title: '文件传输权限',
        meta: {},
        component: permissions
      },
      {
        path: '/terminal/terminalAuthorization/sessionRecords',
        name: 'sessionRecords',
        title: '访问记录',
        meta: {},
        component: sessionRecords
      },
      {
        path: '/terminal/terminalAuthorization/transferRecords',
        name: 'transferRecords',
        title: '文件传输列表',
        meta: {},
        component: transferRecords
      }
    ]
  },
  {
    path: '/terminal/terminalManagement',
    name: 'terminalManagement',
    redirect: '/terminal/terminalManagement/hosts',
    component: terminalManagement,
    children: [
      {
        path: '/terminal/terminalManagement/hosts',
        name: 'hosts',
        title: '终端',
        meta: {},
        component: hosts
      },
      {
        path: '/terminal/terminalManagement/jumpServer',
        name: 'jumpServer',
        title: '跳板机',
        meta: {},
        component: jumpServer
      }
    ]
  }
]
export default router
