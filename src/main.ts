import { app, BrowserWindow } from 'electron';
import { createWindow } from '@actions/windows';

if (require('electron-squirrel-startup')) {
  app.quit();
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('will-quit', () => {});
