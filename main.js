const { app, BrowserWindow } = require("electron");
const { serve } = require("@stlite/desktop");
const path = require("path");

// Start the stlite background server running Pyodide/WebAssembly
const serverPromise = serve();

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "C&W Public Infrastructure Cost Analysis",
    icon: path.join(__dirname, "icon.ico"),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Remove default menu bar for a clean desktop app feel
  mainWindow.setMenu(null);

  // Load the stlite local webserver URL once started
  serverPromise.then((url) => {
    mainWindow.loadURL(url);
  }).catch((err) => {
    console.error("Failed to start stlite server:", err);
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.on("ready", createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow === null) {
    createWindow();
  }
});