'use client';

/**
 * 错误边界组件
 * 
 * 捕获React组件树中的JavaScript错误，显示友好的错误信息
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { ReloadOutlined, HomeOutlined } from '@ant-design/icons';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // 更新state以便下次渲染显示降级UI
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 记录错误到错误报告服务
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // 可以在这里上报错误到监控服务
    // 例如: Sentry.captureException(error);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // 如果提供了自定义fallback，使用它
      if (fallback) {
        return fallback;
      }

      // 默认错误UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-2xl w-full">
            <Result
              status="error"
              title="糟糕！出现了一些问题"
              subTitle={
                <div>
                  <p>我们遇到了一个意外错误，请尝试刷新页面。</p>
                  {process.env.NODE_ENV === 'development' && error && (
                    <details className="mt-4 text-left">
                      <summary className="cursor-pointer text-sm text-gray-600">
                        错误详情（仅开发环境显示）
                      </summary>
                      <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
                        {error.toString()}
                        {this.state.errorInfo && (
                          <>
                            {'\n\n'}
                            {this.state.errorInfo.componentStack}
                          </>
                        )}
                      </pre>
                    </details>
                  )}
                </div>
              }
              extra={[
                <Button
                  key="reload"
                  type="primary"
                  icon={<ReloadOutlined />}
                  onClick={this.handleReset}
                >
                  重新加载
                </Button>,
                <Button
                  key="home"
                  icon={<HomeOutlined />}
                  onClick={this.handleGoHome}
                >
                  返回首页
                </Button>,
              ]}
            />
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;

