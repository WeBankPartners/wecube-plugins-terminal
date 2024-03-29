import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: '/terminalOperation',
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
          path: '/terminalAuthorization/sessionRecords',
          name: 'sessionRecords',
          title: '访问记录',
          meta: {},
          component: () => import('@/pages/authorization/session-records')
        },
        {
          path: '/terminalAuthorization/transferRecords',
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
      redirect: '/terminalManagement/permissions',
      component: () => import('@/pages/terminal-management'),
      children: [
        {
          path: '/terminalManagement/hosts',
          name: 'hosts',
          title: '终端',
          meta: {},
          component: () => import('@/pages/management/hosts')
        },
        {
          path: '/terminalManagement/jumpServer',
          name: 'jumpServer',
          title: '跳板机',
          meta: {},
          component: () => import('@/pages/management/jump-server')
        },
        {
          path: '/terminalManagement/permissions',
          name: 'permissions',
          title: '文件传输权限',
          meta: {},
          component: () => import('@/pages/authorization/permissions')
        }
      ]
    },
    {
      path: '/systemAuthorization',
      name: 'systemAuthorization',
      component: () => import('@/pages/system-authorization')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/login'),
      params: {},
      props: true
    }
  ]
})
