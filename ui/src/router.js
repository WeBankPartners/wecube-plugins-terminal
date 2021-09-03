import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: '/',
      redirect: '/terminal/terminalOperation',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/terminal/terminalOperation',
          name: 'terminalOperation',
          component: () => import('@/pages/terminal-operation'),
          params: {},
          props: true
        }
      ]
    },
    {
      path: '/terminal/terminalAuthorization',
      name: 'terminalAuthorization',
      redirect: '/terminal/terminalAuthorization/sessionRecords',
      component: () => import('@/pages/terminal-authorization'),
      children: [
        {
          path: '/terminal/terminalAuthorization/permissions',
          name: 'permissions',
          title: '文件传输权限',
          meta: {},
          component: () => import('@/pages/authorization/permissions')
        },
        {
          path: '/terminal/terminalAuthorization/sessionRecords',
          name: 'sessionRecords',
          title: '访问记录',
          meta: {},
          component: () => import('@/pages/authorization/session-records')
        },
        {
          path: '/terminal/terminalAuthorization/transferRecords',
          name: 'transferRecords',
          title: '文件传输列表',
          meta: {},
          component: () => import('@/pages/authorization/transfer-records')
        }
      ]
    },
    {
      path: '/terminal/terminalManagement',
      name: 'terminal/terminalManagement',
      redirect: '/terminal/terminalManagement/hosts',
      component: () => import('@/pages/terminal-management'),
      children: [
        {
          path: '/terminal/terminalManagement/hosts',
          name: 'hosts',
          title: '终端',
          meta: {},
          component: () => import('@/pages/management/hosts')
        },
        {
          path: '/terminal/terminalManagement/jumpServer',
          name: 'jumpServer',
          title: '跳板机',
          meta: {},
          component: () => import('@/pages/management/jump-server')
        }
      ]
    },
    {
      path: '/terminal/systemAuthorization',
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
