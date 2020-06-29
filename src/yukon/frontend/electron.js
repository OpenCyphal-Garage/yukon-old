const { app, BrowserWindow, screen } = require('electron')

process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true'

function createWindow () {
  // Create the browser window.
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  const win = new BrowserWindow({
    title: 'Yukon',
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: true
    },
    icon: 'static/images/yukon_logo.png',
    transparent: true
  })

  // and load the index.html of the app.
  win.loadFile('dist/index.html')

  // Open the DevTools.
  // win.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
