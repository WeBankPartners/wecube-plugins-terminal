const manageEditParams = (AddParams, rowparams) => {
  for (let key in AddParams) {
    AddParams[key] = rowparams[key]
  }
  return AddParams
}

const managementUrl = that => {
  let tableParams = that.pageConfig.CRUD
  const pp = {
    __offset: (that.pageConfig.pagination.page - 1) * that.pageConfig.pagination.size,
    __limit: that.pageConfig.pagination.size
  }
  const params = Object.assign({}, pp, that.pageConfig.researchConfig.filters)
  if (params) {
    let tmp = ''
    for (let key in params) {
      tmp = tmp + key + '=' + params[key] + '&'
    }
    tableParams = tableParams + '?' + tmp
  }
  return tableParams
}

export const commonUtil = {
  manageEditParams,
  managementUrl
}
