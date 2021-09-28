export const MENUS = [
  {
    code: 'terminal',
    cnName: '终端',
    enName: 'TERMINAL',
    seqNo: 2,
    parent: '',
    isActive: false,
    submenus: [
      {
        code: 'terminal_console',
        cnName: '终端连接',
        enName: 'TERMINAL CONSOLE',
        isActive: false,
        link: '/terminalOperation'
      }
    ]
  },
  {
    code: 'system',
    cnName: '系统',
    enName: 'SYSTEM',
    seqNo: 1,
    parent: '',
    isActive: false,
    submenus: [
      {
        code: 'system_asset',
        cnName: '终端管理',
        enName: 'TERMINAL ASSET',
        isActive: false,
        link: '/terminalManagement'
      },
      {
        code: 'system_authorization',
        cnName: '系统授权',
        enName: 'TERMINAL AUTHORIZATION',
        isActive: false,
        link: '/systemAuthorization'
      },
      {
        code: 'system_audit',
        cnName: '终端审计',
        enName: 'TERMINAL AUDIT',
        isActive: false,
        link: '/terminalAuthorization'
      }
    ]
  }
]
