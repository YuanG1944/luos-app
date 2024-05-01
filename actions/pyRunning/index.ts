import { exec } from 'child_process';
import path from 'path';

// const dir = process.cwd();

export interface RespType {
  files: {
    path: string;
  }[];
  model: 'RWA' | 'Others' | 'Credit_Limits' | 'Finance';
}

const executablePath = path.join(__dirname, '../../script/microsoft/dist/data_conversion.exe');

const handlePath = (resp: RespType, fn?: () => void) => {
  console.info('resp--->', resp);
  const { files, model } = resp;
  const inputFile = files.map((f) => f.path).join(',');

  exec(
    `${executablePath} --input "${inputFile}" --model ${model} --date 0 --ip 0`,
    (error, stdout) => {
      if (error) {
        console.error(`exec error: ${error}`);
        return;
      }
      console.log(`stdout: ${stdout}`);
      fn && fn();
    },
  );
};

export default {
  handlePath,
};