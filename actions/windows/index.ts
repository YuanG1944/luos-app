import { BrowserWindow, screen, ipcMain, ipcRenderer, globalShortcut, Menu } from 'electron';
import path from 'path';

export const createWindow = () => {
  const mainWindow = new BrowserWindow({
    show: true,
    frame: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      sandbox: false,
    },
  });

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }

  Menu.setApplicationMenu(null);

  // globalShortcut.register('f12', () => {
  mainWindow.webContents.openDevTools();
  // });
};
