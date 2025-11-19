/**
 * 图谱数据缓存 Hook
 * 使用内存缓存优化图谱数据加载
 */

'use client';

import { useCallback, useRef } from 'react';
import { MemoryCache } from '@/lib/performanceUtils';
import type { RelationGraphData, TimelineData } from '@/types/api';

// 创建全局缓存实例
const graphCache = new MemoryCache<string, RelationGraphData>(50);
const timelineCache = new MemoryCache<string, TimelineData>(50);

/**
 * 生成缓存键
 */
function getCacheKey(
  type: 'graph' | 'timeline',
  novelId: number,
  filters?: Record<string, any>
): string {
  const filterStr = filters ? JSON.stringify(filters) : '';
  return `${type}_${novelId}_${filterStr}`;
}

/**
 * 图谱缓存 Hook
 */
export function useGraphCache() {
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map());

  /**
   * 获取或加载图谱数据（带缓存）
   */
  const getOrLoadGraph = useCallback(
    async (
      novelId: number,
      fetcher: () => Promise<RelationGraphData>,
      filters?: Record<string, any>
    ): Promise<RelationGraphData> => {
      const cacheKey = getCacheKey('graph', novelId, filters);

      // 尝试从缓存获取
      const cached = graphCache.get(cacheKey);
      if (cached) {
        return cached;
      }

      // 取消之前的请求（如果有）
      const prevController = abortControllersRef.current.get(cacheKey);
      if (prevController) {
        prevController.abort();
      }

      // 创建新的 AbortController
      const controller = new AbortController();
      abortControllersRef.current.set(cacheKey, controller);

      try {
        // 从API获取
        const data = await fetcher();

        // 存入缓存
        graphCache.set(cacheKey, data, 10 * 60 * 1000); // 10分钟

        // 清理 controller
        abortControllersRef.current.delete(cacheKey);

        return data;
      } catch (error) {
        // 清理 controller
        abortControllersRef.current.delete(cacheKey);
        throw error;
      }
    },
    []
  );

  /**
   * 获取或加载时间线数据（带缓存）
   */
  const getOrLoadTimeline = useCallback(
    async (
      novelId: number,
      fetcher: () => Promise<TimelineData>,
      filters?: Record<string, any>
    ): Promise<TimelineData> => {
      const cacheKey = getCacheKey('timeline', novelId, filters);

      // 尝试从缓存获取
      const cached = timelineCache.get(cacheKey);
      if (cached) {
        return cached;
      }

      // 取消之前的请求（如果有）
      const prevController = abortControllersRef.current.get(cacheKey);
      if (prevController) {
        prevController.abort();
      }

      // 创建新的 AbortController
      const controller = new AbortController();
      abortControllersRef.current.set(cacheKey, controller);

      try {
        // 从API获取
        const data = await fetcher();

        // 存入缓存
        timelineCache.set(cacheKey, data, 10 * 60 * 1000); // 10分钟

        // 清理 controller
        abortControllersRef.current.delete(cacheKey);

        return data;
      } catch (error) {
        // 清理 controller
        abortControllersRef.current.delete(cacheKey);
        throw error;
      }
    },
    []
  );

  /**
   * 清除指定小说的缓存
   */
  const clearNovelCache = useCallback((novelId: number) => {
    // 清除图谱缓存
    graphCache.clear();
    // 清除时间线缓存
    timelineCache.clear();
  }, []);

  /**
   * 清除所有缓存
   */
  const clearAllCache = useCallback(() => {
    graphCache.clear();
    timelineCache.clear();
  }, []);

  return {
    getOrLoadGraph,
    getOrLoadTimeline,
    clearNovelCache,
    clearAllCache,
  };
}

