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

// Wecube Api
export const getAllRoles = () => req.get(`/platform/v1/roles/retrieve`)

export const getTableData = url => req.get(url)
export const addTableRow = (url, data) => req.post(`${url}`, data)
export const editTableRow = (url, id, data) => req.patch(`${url}/${id}`, data)
export const deleteTableRow = (url, id) => req.delete(`${url}/${id}`)

export const getHost = () => req.get(`/terminal/v1/assets`)

export const getAssets = () => req.get(`/terminal/v1/view-assets`)

export const savePermission = data => req.post(`/terminal/v1/permissions`, data)
export const editPermissions = (id, data) => req.patch(`/terminal/v1/permissions/${id}`, data)
