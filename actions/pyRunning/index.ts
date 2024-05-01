import { exec } from 'child_process';
import path from 'path';

// const dir = process.cwd();

export interface RespType {
  files: {
    path: string;
  }[];
  model: 'RWA' | 'Others' | 'Credit_Limits' | 'Finance';
}

let executablePath = '';

if (process.platform === 'darwin') {
  executablePath = path.join(__dirname, '../../script/apple/dist/data_conversion');
}

if (process.platform === 'win32') {
  executablePath = path.join(__dirname, '../../script/microsoft/dist/data_conversion.exe');
}

const handlePath = (resp: RespType, fn?: () => void, errFn?: () => void) => {
  if (executablePath) {
    const { files, model } = resp;
    const inputFile = files.map((f) => f.path).join(',');

    exec(
      `${executablePath} --input "${inputFile}" --model ${model} --date 0 --ip 0`,
      (error, stdout) => {
        if (error) {
          console.error(`exec error: ${error}`);
          errFn && errFn();
          return;
        }
        console.log(`stdout: ${stdout}`);
        fn && fn();
      },
    );
  }
};

export default {
  handlePath,
};
