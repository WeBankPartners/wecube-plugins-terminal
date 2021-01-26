import Index from '@/pages/index'
import terminalOperation from '@/pages/terminal-operation'
import terminalManagement from '@/pages/terminal-management'
import permissions from '@/pages/management/permissions'
import sessionRecords from '@/pages/management/session-records'
import transferRecords from '@/pages/management/transfer-records'

const router = [
  {
    path: '/terminalOperation',
    name: 'terminalOperation',
    redirect: 'terminalOperation',
    component: Index,
    children: [
      {
        path: '/terminalOperation',
        name: 'terminalOperation',
        component: terminalOperation,
        params: {},
        props: true
      }
    ]
  },
  {
    path: '/terminalManagement',
    name: 'terminalManagement',
    redirect: '/terminalManagement/sessionRecords',
    component: terminalManagement,
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
  }
]
export default router
