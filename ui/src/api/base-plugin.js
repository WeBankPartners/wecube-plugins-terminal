export const pluginErrorMessage = async r => {
  // const res = await r
  // if (res.status.startsWith('ERR')) {
  //   const errorMes = Array.isArray(res.data) ? res.data.map(_ => _.error).join('<br/>') : res.message
  //   window.vm &&
  //     window.vm.$Notice.error({
  //       title: 'Error',
  //       desc: errorMes,
  //       duration: 0
  //     })
  // }
  return r
}
