const fileId = localStorage.getItem('fileId')
const token = localStorage.getItem('replayToken')
var headers = new Headers({
  Authorization: 'Bearer ' + token
})
var req = new Request(`/terminal/v1/session-records/${fileId}/file`, { method: 'GET', headers: headers, mode: 'cors' })
const div = document.getElementById('app')
// eslint-disable-next-line no-undef
const player = new XtermPlayer.XtermPlayer(req, div)
console.log(player)
