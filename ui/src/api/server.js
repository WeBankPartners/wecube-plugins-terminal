import { req as request, baseURL } from './base'
import { pluginErrorMessage } from './base-plugin'
let req = request
if (window.request) {
  req = {
    post: (url, ...params) => pluginErrorMessage(window.request.post(baseURL + url, ...params)),
    get: (url, ...params) => pluginErrorMessage(window.request.get(baseURL + url, ...params)),
    delete: (url, ...params) => pluginErrorMessage(window.request.delete(baseURL + url, ...params)),
    put: (url, ...params) => pluginErrorMessage(window.request.put(baseURL + url, ...params)),
    patch: (url, ...params) => pluginErrorMessage(window.request.patch(baseURL + url, ...params))
  }
}

export const getRoleList = () => req.get(`/platform/v1/roles/retrieve`)
export const getRolesByCurrentUser = () => req.get(`/platform/v1/users/roles`)

// Wecube Api
export const getAllRoles = () => req.get(`/platform/v1/roles/retrieve`)

export const getTableData = url => req.get(url)
export const addTableRow = (url, data) => req.post(`${url}`, data)
export const editTableRow = (url, id, data) => req.patch(`${url}/${id}`, data)
export const deleteTableRow = (url, id) => req.delete(`${url}/${id}`)

export const getHost = () => req.get(`/terminal/v1/assets`)

export const getAssets = () => req.get(`/terminal/v1/view-assets`)
export const getAssetsByExpression = data => {
  const params = {
    expression: data
  }
  return req.get(`/terminal/v1/assets`, { params })
}
export const getFileManagementPermission = id => req.get(`/terminal/v1/assets/${id}/permissions`)

export const savePermission = data => req.post(`/terminal/v1/permissions`, data)
export const editPermissions = (id, data) => req.patch(`/terminal/v1/permissions/${id}`, data)

export const addCollection = data => req.post(`/terminal/v1/bookmarks`, data)
export const getTargetOptions = (pkgName, entityName) =>
  req.post(`/${pkgName}/entities/${entityName}/query`, {
    additionalFilters: []
  })
export const getEntityRefsByPkgNameAndEntityName = (pkgName, entityName) =>
  req.get(`/platform/v1/models/package/${pkgName}/entity/${entityName}`)
export const getAllDataModels = () => req.get(`/platform/v1/models`)

export const getFavoritesList = () => req.get(`/terminal/v1/bookmarks`)
export const deleteFavorites = id => req.delete(`/terminal/v1/bookmarks/${id}`)
export const editCollection = (id, data) => req.patch(`/terminal/v1/bookmarks/${id}`, data)

export const getMgmtAssets = () => req.get(`/terminal/v1/mgmt-assets`)
export const addMgmtAssets = data => req.post(`/terminal/v1/mgmt-assets`, data)
export const deleteMgmtAssets = id => req.delete(`/terminal/v1/mgmt-assets/${id}`)
export const editMgmtAssets = (id, data) => req.patch(`/terminal/v1/mgmt-assets/${id}`, data)
