export const MENUS = [
  {
    code: 'terminal',
    cnName: '终端',
    enName: 'TERMINAL',
    seqNo: 2,
    parent: '',
    isActive: 'yes'
  },
  {
    code: 'system',
    cnName: '系统',
    enName: 'SYSTEM',
    seqNo: 2,
    parent: '',
    isActive: 'yes'
  },
  {
    code: 'terminal_console',
    cnName: '终端连接',
    enName: 'TERMINAL CONSOLE',
    seqNo: 1,
    parent: 'TERMINAL',
    isActive: 'yes',
    link: '/terminalOperation'
  },
  {
    code: 'terminal_asset',
    cnName: '终端管理',
    enName: 'TERMINAL ASSET',
    seqNo: 1,
    parent: 'system',
    isActive: 'yes',
    link: '/terminalManagement'
  },
  {
    code: 'terminal_authorization',
    cnName: '系统授权',
    enName: 'TERMINAL AUTHORIZATION',
    seqNo: 2,
    parent: 'system',
    isActive: 'yes',
    link: '/systemAuthorization'
  },
  {
    code: 'terminal_permission',
    cnName: '终端授权',
    enName: 'TERMINAL PERMISSION',
    seqNo: 3,
    parent: 'system',
    isActive: 'yes',
    link: '/terminalAuthorization'
  }
]
