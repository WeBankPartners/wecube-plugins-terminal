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
      path: '/terminalAuthorization',
      name: 'terminalAuthorization',
      redirect: '/terminalAuthorization/sessionRecords',
      component: () => import('@/pages/terminal-authorization'),
      children: [
        {
          path: 'permissions',
          name: 'permissions',
          title: '文件传输权限',
          meta: {},
          component: () => import('@/pages/authorization/permissions')
        },
        {
          path: 'sessionRecords',
          name: 'sessionRecords',
          title: '访问记录',
          meta: {},
          component: () => import('@/pages/authorization/session-records')
        },
        {
          path: 'transferRecords',
          name: 'transferRecords',
          title: '文件传输列表',
          meta: {},
          component: () => import('@/pages/authorization/transfer-records')
        }
      ]
    },
    {
      path: '/terminalManagement',
      name: 'terminalManagement',
      redirect: '/terminalManagement/hosts',
      component: () => import('@/pages/terminal-management'),
      children: [
        {
          path: 'hosts',
          name: 'hosts',
          title: '终端',
          meta: {},
          component: () => import('@/pages/management/hosts')
        },
        {
          path: 'jumpServer',
          name: 'jumpServer',
          title: '跳板机',
          meta: {},
          component: () => import('@/pages/management/jump-server')
        }
      ]
    },
    {
      path: '/systemAuthorization',
      name: '/systemAuthorization',
      component: () => import('@/pages/system-authorization')
    }
  ]
})
