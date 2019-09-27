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
