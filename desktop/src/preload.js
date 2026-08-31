const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("brew", {
  meta: () => ipcRenderer.invoke("brew:meta"),
  catalog: () => ipcRenderer.invoke("brew:catalog"),
  inspect: (home) => ipcRenderer.invoke("brew:inspect", home),
  env: () => ipcRenderer.invoke("brew:env"),
  run: (payload) => ipcRenderer.invoke("brew:run", payload),
  deployAll: (payload) => ipcRenderer.invoke("brew:deploy-all", payload),
  restoreAll: (payload) => ipcRenderer.invoke("brew:restore-all", payload),
  accept: (payload) => ipcRenderer.invoke("brew:accept", payload),
  setup: () => ipcRenderer.invoke("brew:setup"),
  choose: () => ipcRenderer.invoke("brew:choose"),
  open: (folder) => ipcRenderer.invoke("brew:open", folder),
  copy: (text) => ipcRenderer.invoke("brew:copy", text),
  external: (url) => ipcRenderer.invoke("brew:external", url),
  setBlade: (id) => ipcRenderer.invoke("brew:blade", id),
  minimize: () => ipcRenderer.invoke("win:min"),
  toggleMaximize: () => ipcRenderer.invoke("win:max"),
  close: () => ipcRenderer.invoke("win:close"),
  onLog: (fn) => {
    const listener = (_event, entry) => fn(entry);
    ipcRenderer.on("brew:log", listener);
    return () => ipcRenderer.removeListener("brew:log", listener);
  },
});
