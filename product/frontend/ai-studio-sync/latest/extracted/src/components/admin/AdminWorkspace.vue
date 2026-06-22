<script setup lang="ts">
import { Bot, ShieldCheck } from 'lucide-vue-next';
</script>

<template>
  <div class="p-8 max-w-md mx-auto min-h-screen flex flex-col items-center justify-center text-center text-zinc-600 bg-zinc-50 font-sans">
    <div class="w-16 h-16 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 border shadow-sm">
      <Bot :size="30" />
    </div>
    <h1 class="text-lg font-serif font-black text-zinc-800">易学管理工作台 · Admin Space</h1>
    <p class="text-xs text-zinc-500 mt-2 leading-relaxed max-w-xs">
      该子系统模块属于「EaseWise后台治理区」，不属于移动 H5 客户端。
    </p>

    <div class="mt-6 border border-thin bg-white rounded-xl p-4 text-left max-w-xs select-none">
      <div class="flex gap-2 items-center text-emerald-600 font-bold text-xs mb-1.5">
        <ShieldCheck :size="13" />
        <span>安全隔离区已部署</span>
      </div>
      <p class="text-[10.5px] text-zinc-400 leading-normal">
        所有管理功能、统计图表日志及全域公共福利码（Claim URL）在生产环境被完整隔离防护，不混杂移动原型逻辑。
      </p>
    </div>
  </div>
</template>
