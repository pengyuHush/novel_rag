/**
 * 设置页面
 * 包含API配置、默认模型、Token统计等设置
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { ModelType, type AppConfig, type TokenStatsResponse } from '@/types/api';

export default function SettingsPage() {
  const router = useRouter();
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [tokenStats, setTokenStats] = useState<TokenStatsResponse | null>(null);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadConfig();
    loadTokenStats();
  }, []);

  const loadConfig = async () => {
    try {
      const configData = await api.getConfig();
      setConfig(configData);
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadTokenStats = async () => {
    try {
      const stats = await api.getTokenStats({ period: 'month' });
      setTokenStats(stats);
    } catch (error) {
      console.error('Failed to load token stats:', error);
    }
  };

  const handleTestConnection = async () => {
    if (!apiKey) {
      toast.error('请输入API Key');
      return;
    }

    try {
      setIsTestingConnection(true);
      setConnectionStatus('idle');
      const result = await api.testConnection({ apiKey });
      if (result.success) {
        setConnectionStatus('success');
        toast.success('连接测试成功');
      } else {
        setConnectionStatus('error');
        toast.error(result.message || '连接测试失败');
      }
    } catch (error) {
      setConnectionStatus('error');
      toast.error('连接测试失败');
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!config) return;

    try {
      setIsSaving(true);
      await api.updateConfig(config);
      toast.success('设置已保存');
    } catch (error) {
      console.error('Failed to save config:', error);
      toast.error('保存设置失败');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">
      {/* 返回按钮 */}
      <Button
        variant="ghost"
        onClick={() => router.push('/')}
        className="mb-4"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        返回主页
      </Button>

      <h1 className="text-3xl font-bold">系统设置</h1>

      {/* API配置 */}
      <Card>
        <CardHeader>
          <CardTitle>智谱AI配置</CardTitle>
          <CardDescription>
            配置智谱AI API Key以使用大模型服务
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">API Key</label>
            <div className="flex gap-2">
              <Input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="请输入智谱AI API Key"
                className="flex-1"
              />
              <Button
                onClick={handleTestConnection}
                disabled={isTestingConnection || !apiKey}
                variant="outline"
              >
                {isTestingConnection ? '测试中...' : '测试连接'}
              </Button>
            </div>
            {connectionStatus === 'success' && (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle className="h-4 w-4" />
                连接成功
              </div>
            )}
            {connectionStatus === 'error' && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <XCircle className="h-4 w-4" />
                连接失败
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground">
            请访问{' '}
            <a
              href="https://open.bigmodel.cn/usercenter/apikeys"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
            >
              智谱AI控制台
            </a>{' '}
            获取API Key
          </p>
        </CardContent>
      </Card>

      {/* 模型配置 */}
      {config && (
        <Card>
          <CardHeader>
            <CardTitle>模型配置</CardTitle>
            <CardDescription>设置默认使用的大语言模型</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">默认模型</label>
              <Select
                value={config.defaultModel}
                onValueChange={(value) =>
                  setConfig({ ...config, defaultModel: value as ModelType })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ModelType.GLM_4_5_FLASH}>
                    GLM-4.5-Flash（免费）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_FLASH}>
                    GLM-4-Flash（免费，128K）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_5_AIR}>
                    GLM-4.5-Air（推荐）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_5_AIRX}>
                    GLM-4.5-AirX（增强）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_5_X}>
                    GLM-4.5-X（极速）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_5}>
                    GLM-4.5（高性能）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_PLUS}>
                    GLM-4-Plus（顶级）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_6}>
                    GLM-4.6（旗舰）
                  </SelectItem>
                  <SelectItem value={ModelType.GLM_4_LONG}>
                    GLM-4-Long（百万上下文）
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button onClick={handleSaveConfig} disabled={isSaving}>
              {isSaving ? '保存中...' : '保存设置'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Token统计 */}
      {tokenStats && (
        <Card>
          <CardHeader>
            <CardTitle>Token统计</CardTitle>
            <CardDescription>本月Token使用情况</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">总消耗</p>
                <p className="text-2xl font-bold">
                  {tokenStats.total_tokens.toLocaleString()}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">预估成本</p>
                <p className="text-2xl font-bold">
                  ¥{tokenStats.total_cost.toFixed(2)}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">统计周期</p>
                <p className="text-2xl font-bold">{tokenStats.period}</p>
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="text-sm font-medium mb-3">按模型分类</h4>
              <div className="space-y-2">
                {tokenStats.by_model && Object.entries(tokenStats.by_model).map(([model, stats]) => (
                  <div key={model} className="flex justify-between items-center">
                    <Badge variant="outline">{model}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {(stats as any).totalTokens?.toLocaleString() || 0} tokens
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="text-sm font-medium mb-3">按操作分类</h4>
              <div className="space-y-2">
                {tokenStats.by_operation && Object.entries(tokenStats.by_operation).map(([operation, stats]) => (
                  <div key={operation} className="flex justify-between items-center">
                    <Badge variant="secondary">
                      {operation === 'index' ? '索引' : '查询'}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {(stats as any).totalTokens?.toLocaleString() || 0} tokens
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

