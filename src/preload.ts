import pyRunning from '@actions/pyRunning';
import { contextBridge } from 'electron';

contextBridge.exposeInMainWorld('eBridge', {
  handlePath: pyRunning.handlePath,
});
