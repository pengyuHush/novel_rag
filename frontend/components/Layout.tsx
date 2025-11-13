/**
 * 主布局组件
 * 提供整体页面结构：Header + Sidebar + Content
 */

'use client';

import React from 'react';
import { Layout as AntLayout, theme } from 'antd';
import Navigation from './Navigation';

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* 顶部标题栏 */}
      <Header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1,
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          background: colorBgContainer,
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <div style={{ fontSize: '20px', fontWeight: 'bold', marginRight: '24px' }}>
          📚 网络小说智能问答系统
        </div>
      </Header>

      <AntLayout>
        {/* 左侧导航栏 */}
        <Sider
          width={200}
          style={{
            background: colorBgContainer,
            borderRight: '1px solid #f0f0f0',
          }}
        >
          <Navigation />
        </Sider>

        {/* 主内容区 */}
        <Content
          style={{
            padding: 24,
            margin: 0,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;

