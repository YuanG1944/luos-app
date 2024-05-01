import { FC } from 'react';
import styles from './index.module.scss';
import Contents from '@/views/Contents';

const Layout: FC = () => {
  return (
    <div id="root">
      <div className={styles.layout}>
        <Contents />
      </div>
    </div>
  );
};
export default Layout;
