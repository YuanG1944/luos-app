import React, { useState } from 'react';
import { UploadOutlined } from '@ant-design/icons';
import { Form, message, Radio, UploadFile, UploadProps } from 'antd';
import { Button, Upload } from 'antd';
import { RcFile } from 'antd/es/upload';
import styles from './index.module.scss';
import { useForm } from 'antd/es/form/Form';

export const modelList = [
  {
    label: 'RWA',
    value: 'RWA',
  },
  {
    label: 'Others',
    value: 'Others',
  },
  {
    label: 'Credit Limits',
    value: 'Credit_Limits',
  },
  {
    label: 'Finance',
    value: 'Finance',
  },
];

const UploadFilePath: React.FC = () => {
  const [form] = useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [runningLoading, setRunningLoading] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const handleChange: UploadProps['customRequest'] = (uploadInfo) => {
    const file = uploadInfo.file as RcFile;
    if (fileList.find((f) => f.name === file.name)) {
      return messageApi.open({
        type: 'warning',
        content: '请勿上传重复文件',
      });
    }
    setFileList((f) => [...f, file]);
  };

  const handleRemove: UploadProps['onRemove'] = (file) => {
    setFileList((item) => item.filter((f) => f.uid !== file.uid));
  };

  const handleRunning = () => {
    form
      .validateFields({ validateOnly: true })
      .then(() => {
        if (!fileList.length) {
          return messageApi.open({
            type: 'warning',
            content: '请上传文件',
          });
        }
        setRunningLoading(true);
        window?.eBridge?.handlePath(
          {
            model: form.getFieldValue('model'),
            files: fileList,
          },
          () => {
            setRunningLoading(false);
          },
        );
      })
      .catch((err) => {
        console.error('handleRunning err: ', err);
        setRunningLoading(false);
      });
  };

  return (
    <div className={styles.contents}>
      <div className={styles.formBox}>
        <Form form={form} onFinish={handleRunning}>
          <Form.Item
            required
            rules={[{ required: true, message: 'Mode is required.' }]}
            label="Model"
            name="model"
          >
            <Radio.Group>
              {modelList.map((md) => (
                <Radio value={md.value} key={md.value}>
                  {md.label}
                </Radio>
              ))}
            </Radio.Group>
          </Form.Item>
          <Form.Item required label="Upload File" name="files">
            <Upload
              accept=".xls, .xlsx"
              multiple={false}
              customRequest={handleChange}
              onRemove={handleRemove}
              fileList={fileList}
            >
              <Button icon={<UploadOutlined />}>Upload</Button>
            </Upload>
          </Form.Item>

          <div className={styles.footer}>
            <Form.Item>
              <Button loading={runningLoading} type="primary" htmlType="submit">
                Running
              </Button>
            </Form.Item>
          </div>
        </Form>
      </div>

      {contextHolder}
    </div>
  );
};

export default UploadFilePath;
