Как установить уровень логгирования:

```js
const logLevels = {
  'trace': log.levels.TRACE,
  'debug': log.levels.DEBUG,
  'info': log.levels.INFO,
  'warn': log.levels.WARN,
}
let logLevelStr = localStorage.getItem('logLevel') || '';
```


Поменять настройки websocket

```js
let websocketAddress = localStorage.getItem('websocket') || 'ws://127.0.0.1:8000/ws';
```


Формат сообщений. Ожидается сообщения в формате JSON:
```js
{
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
  ]
}
```
