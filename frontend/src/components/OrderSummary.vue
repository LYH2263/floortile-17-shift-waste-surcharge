<script setup>
import { hourToTime } from '../api'

defineProps({
  result: { type: Object, default: null },
})

function fmtHour(v) {
  return v === null || v === undefined ? '—' : hourToTime(v)
}
</script>
<template>
  <div v-if="result" class="order-summary">
    <div class="hero">{{ result.order_count }} 片</div>
    <ul>
      <li>净用量 {{ result.raw_count }} 片，地面 {{ result.area_m2 }} m²，单砖 {{ result.piece_m2 }} m²</li>
      <li>
        采用损耗 <strong>{{ result.waste_pct }}%</strong>
        <template v-if="result.surcharge_pct">
          （基础 {{ result.base_waste_pct }}% + 班次加耗 {{ result.surcharge_pct }}%，班次：{{ result.shift_name }}）
        </template>
      </li>
      <li>施工钟点 {{ fmtHour(result.work_time) }}</li>
    </ul>
  </div>
</template>
