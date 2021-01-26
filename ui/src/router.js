import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: 'terminalOperation',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/terminalOperation',
          name: 'terminalOperation',
          component: () => import('@/pages/terminal-operation'),
          params: {},
          props: true
        }
      ]
    },
    {
      path: '/terminalManagement',
      name: 'terminalManagement',
      redirect: '/terminalManagement/sessionRecords',
      component: () => import('@/pages/terminal-management'),
      children: [
        {
          path: 'permissions',
          name: 'permissions',
          title: '文件传输权限',
          meta: {},
          component: () => import('@/pages/management/permissions')
        },
        {
          path: 'sessionRecords',
          name: 'sessionRecords',
          title: '访问记录',
          meta: {},
          component: () => import('@/pages/management/session-records')
        },
        {
          path: 'transferRecords',
          name: 'transferRecords',
          title: '文件传输列表',
          meta: {},
          component: () => import('@/pages/management/transfer-records')
        }
      ]
    }
  ]
})
