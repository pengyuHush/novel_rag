/**
 * 导航组件
 * 左侧边栏导航菜单
 */

'use client';

import React from 'react';
import { Menu } from 'antd';
import {
  BookOutlined,
  QuestionCircleOutlined,
  ReadOutlined,
  PartitionOutlined,
  SettingOutlined,
  BarChartOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { useRouter, usePathname } from 'next/navigation';
import type { MenuProps } from 'antd';

type MenuItem = Required<MenuProps>['items'][number];

const Navigation: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();

  const items: MenuItem[] = [
    {
      key: '/novels',
      icon: <BookOutlined />,
      label: '小说管理',
    },
    {
      key: '/query',
      icon: <QuestionCircleOutlined />,
      label: '智能问答',
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '查询历史',
    },
    {
      key: '/reader',
      icon: <ReadOutlined />,
      label: '在线阅读',
    },
    {
      key: '/graph',
      icon: <PartitionOutlined />,
      label: '可视化分析',
    },
    {
      key: '/stats',
      icon: <BarChartOutlined />,
      label: 'Token统计',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    router.push(e.key);
  };

  // 获取当前选中的菜单项
  const selectedKeys = [pathname];

  return (
    <Menu
      mode="inline"
      selectedKeys={selectedKeys}
      items={items}
      onClick={handleMenuClick}
      style={{ height: '100%', borderRight: 0 }}
    />
  );
};

export default Navigation;

