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
    path: '/terminalOperation',
    name: '/terminalOperation',
    component: terminalOperation,
    params: {},
    props: true
  },
  {
    path: '/terminalAuthorization',
    name: 'terminalAuthorization',
    redirect: '/terminalAuthorization/sessionRecords',
    component: terminalAuthorization,
    children: [
      {
        path: 'permissions',
        name: 'permissions',
        title: '文件传输权限',
        meta: {},
        component: permissions
      },
      {
        path: 'sessionRecords',
        name: 'sessionRecords',
        title: '访问记录',
        meta: {},
        component: sessionRecords
      },
      {
        path: 'transferRecords',
        name: 'transferRecords',
        title: '文件传输列表',
        meta: {},
        component: transferRecords
      }
    ]
  },
  {
    path: '/terminalManagement',
    name: 'terminalManagement',
    redirect: '/terminalManagement/hosts',
    component: terminalManagement,
    children: [
      {
        path: 'hosts',
        name: 'hosts',
        title: '终端',
        meta: {},
        component: hosts
      },
      {
        path: 'jumpServer',
        name: 'jumpServer',
        title: '跳板机',
        meta: {},
        component: jumpServer
      }
    ]
  }
]
export default router
