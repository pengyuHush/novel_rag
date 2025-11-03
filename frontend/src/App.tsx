import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import SearchPage from './pages/SearchPage';
import GraphPage from './pages/GraphPage';
import ReaderPage from './pages/ReaderPage';
import './App.css';

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // 纸质书籍风格的配色方案
          colorPrimary: '#8B6914', // 深金棕色
          colorBgLayout: '#FAF8F3', // 纸张米黄色背景
          colorBgContainer: '#FFFEF9', // 容器背景（更白一些的纸色）
          colorBorder: '#E8E3D6', // 边框颜色
          colorText: '#3D3D3D', // 主文字颜色
          colorTextSecondary: '#8B7355', // 次要文字颜色
          borderRadius: 12, // 更圆润的边角
          fontSize: 14,
          fontFamily: "'Noto Serif SC', 'Songti SC', 'SimSun', serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC'",
        },
        components: {
          Layout: {
            headerBg: '#FFFEF9',
            bodyBg: '#FAF8F3',
          },
          Button: {
            colorPrimary: '#8B6914',
            colorPrimaryHover: '#A67C1A',
            controlHeight: 36,
            fontWeight: 500,
          },
          Input: {
            colorBgContainer: '#FFFEF9',
            colorBorder: '#D4CFBF',
            activeShadow: '0 0 0 2px rgba(139, 105, 20, 0.1)',
          },
          Card: {
            colorBgContainer: '#FFFEF9',
            boxShadowTertiary: '0 2px 8px rgba(139, 105, 20, 0.08)',
          },
          Menu: {
            colorBgContainer: '#FFFEF9',
            colorItemBgSelected: '#F5EFE0',
            colorItemTextSelected: '#8B6914',
          },
        },
        algorithm: theme.defaultAlgorithm,
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/graph/:novelId" element={<GraphPage />} />
          <Route path="/reader/:novelId" element={<ReaderPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
