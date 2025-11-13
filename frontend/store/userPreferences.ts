/**
 * 用户偏好设置存储
 * 
 * 使用localStorage持久化用户配置
 */

import { ModelType } from '@/types/query';

interface UserPreferences {
  defaultModel: ModelType;
  apiKey?: string;
  theme?: 'light' | 'dark';
  language?: 'zh-CN' | 'en-US';
}

const STORAGE_KEY = 'novel_rag_user_preferences';

/**
 * 获取用户偏好设置
 */
export function getUserPreferences(): Partial<UserPreferences> {
  if (typeof window === 'undefined') {
    return {};
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to load user preferences:', error);
  }

  return {};
}

/**
 * 保存用户偏好设置
 */
export function saveUserPreferences(preferences: Partial<UserPreferences>): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const current = getUserPreferences();
    const updated = { ...current, ...preferences };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to save user preferences:', error);
  }
}

/**
 * 获取默认模型
 */
export function getDefaultModel(): ModelType {
  const prefs = getUserPreferences();
  return prefs.defaultModel || ModelType.GLM_4_5_AIR;
}

/**
 * 保存默认模型
 */
export function saveDefaultModel(model: ModelType): void {
  saveUserPreferences({ defaultModel: model });
}

/**
 * 获取API Key
 */
export function getApiKey(): string | undefined {
  const prefs = getUserPreferences();
  return prefs.apiKey;
}

/**
 * 保存API Key
 */
export function saveApiKey(apiKey: string): void {
  saveUserPreferences({ apiKey });
}

/**
 * 清除所有用户偏好设置
 */
export function clearUserPreferences(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear user preferences:', error);
  }
}

