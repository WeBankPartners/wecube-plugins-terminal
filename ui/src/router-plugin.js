import terminalOperation from '@/pages/terminal-operation'
import terminalManagement from '@/pages/terminal-management'
import permissions from '@/pages/authorization/permissions'
import sessionRecords from '@/pages/authorization/session-records'
import transferRecords from '@/pages/authorization/transfer-records'
import terminalAuthorization from '@/pages/terminal-authorization'
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
    redirect: '/terminalManagement/permissions',
    component: terminalManagement,
    children: [
      {
        path: 'jumpServer',
        name: 'jumpServer',
        title: '跳板机',
        meta: {},
        component: jumpServer
      },
      {
        path: 'permissions',
        name: 'permissions',
        title: '',
        meta: {},
        component: permissions
      }
    ]
  }
]
export default router
