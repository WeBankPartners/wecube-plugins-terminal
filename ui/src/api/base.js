import { setCookie, getCookie, clearCookie } from '@/pages/util/cookie'
import Vue from 'vue'
import axios from 'axios'
export const baseURL = ''
export const req = axios.create({
  withCredentials: true,
  baseURL,
  timeout: 50000
})
let refreshRequest = null
req.interceptors.request.use(
  config => {
    return new Promise((resolve, reject) => {
      const currentTime = new Date().getTime()
      const accessToken = getCookie('accessToken')
      if (accessToken && config.url !== '/terminal/v1/login') {
        const expiration = getCookie('accessTokenExpirationTime') * 1 - currentTime
        if (expiration < 1 * 60 * 1000 && !refreshRequest) {
          refreshRequest = axios.get('/terminal/v1/refresh-token', {
            headers: {
              Authorization: 'Bearer ' + getCookie('refreshToken')
            }
          })
          refreshRequest.then(
            res => {
              setCookie(res.data.data)
              config.headers.Authorization = 'Bearer ' + res.data.data.find(t => t.tokenType === 'accessToken').token
              refreshRequest = null
              resolve(config)
            },
            // eslint-disable-next-line handle-callback-err
            err => {
              refreshRequest = null
              window.location.href = window.location.origin + window.location.pathname + '#/login'
            }
          )
        }
        if (expiration < 1 * 60 * 1000 && refreshRequest) {
          refreshRequest.then(
            res => {
              setCookie(res.data.data)
              config.headers.Authorization = 'Bearer ' + res.data.data.find(t => t.tokenType === 'accessToken').token
              refreshRequest = null
              resolve(config)
            },
            // eslint-disable-next-line handle-callback-err
            err => {
              refreshRequest = null
              window.location.href = window.location.origin + window.location.pathname + '#/login'
            }
          )
        }
        if (expiration > 1 * 60 * 1000) {
          config.headers.Authorization = 'Bearer ' + accessToken
          resolve(config)
        }
      } else {
        resolve(config)
      }
    })
  },
  error => {
    return Promise.reject(error)
  }
)

const throwError = res => new Error(res.message || 'error')
req.interceptors.response.use(
  res => {
    if (res.status === 200) {
      if (res.data.status.startsWith('ERR')) {
        const errorMes = Array.isArray(res.data.data)
          ? res.data.data.map(_ => _.message).join('<br/>')
          : res.data.message
        Vue.prototype.$Notice.error({
          title: 'Error',
          desc: errorMes,
          duration: 10
        })
      }
      return {
        ...res.data,
        user: res.headers['username'] || ' - '
      }
    } else {
      return {
        data: throwError(res)
      }
    }
  },
  error => {
    const { response } = error
    if (response.status === 401 && error.config.url !== '/terminal/api/v1/login') {
      let refreshToken = getCookie('refreshToken')
      if (refreshToken.length > 0) {
        let refreshRequest = axios.get('/terminal/v1/refresh-token', {
          headers: {
            Authorization: 'Bearer ' + refreshToken
          }
        })
        return refreshRequest.then(
          resRefresh => {
            setCookie(resRefresh.data.data)
            // replace token with new one and replay request
            error.config.headers.Authorization = 'Bearer ' + getCookie('accessToken')
            error.config.url = error.config.url.replace('/terminal/api/v1', '')
            let retryRequest = axios(error.config)
            return retryRequest.then(
              res => {
                if (res.status === 200) {
                  // do request success again
                  if (res.data.status === 'ERROR') {
                    const errorMes = Array.isArray(res.data.data)
                      ? res.data.data.map(_ => _.message || _.errorMessage).join('<br/>')
                      : res.data.message
                    Vue.prototype.$Notice.warning({
                      title: 'Error',
                      desc: errorMes,
                      duration: 10
                    })
                  }
                  // if (
                  //   res.headers['content-type'] === 'application/octet-stream' &&
                  //   res.request.responseURL.includes('/platform/')
                  // ) {
                  //   exportFile(res)
                  //   Vue.prototype.$Notice.info({
                  //     title: 'Success',
                  //     desc: '',
                  //     duration: 10
                  //   })
                  //   return
                  // }
                  return res.data instanceof Array ? res.data : { ...res.data }
                } else {
                  return {
                    data: throwError(res)
                  }
                }
              },
              err => {
                const { response } = err
                return new Promise((resolve, reject) => {
                  resolve({
                    data: throwError(response)
                  })
                })
              }
            )
          },
          // eslint-disable-next-line handle-callback-err
          errRefresh => {
            clearCookie('refreshToken')
            window.location.href = window.location.origin + window.location.pathname + '#/login'
            return {
              data: {} // throwError(errRefresh.response)
            }
          }
        )
      } else {
        window.location.href = window.location.origin + window.location.pathname + '#/login'
      }
    }
    // const { response } = error
    // Vue.prototype.$Notice.error({
    //   title: 'error',
    //   duration: 10,
    //   desc:
    //     (response.data &&
    //       'status:' +
    //         response.data.status +
    //         '<br/> error:' +
    //         response.data.error +
    //         '<br/> message:' +
    //         response.data.message) ||
    //     'error'
    // })
    return new Promise((resolve, reject) => {
      resolve({
        data: throwError(error)
      })
    })
  }
)

function setHeaders (obj) {
  Object.keys(obj).forEach(key => {
    req.defaults.headers.common[key] = obj[key]
  })
}

export { setHeaders }
