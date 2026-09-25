<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, hourToTime } from '../api'

const items = ref([])
const selected = ref(null)
const err = ref('')

onMounted(async () => { items.value = (await getJSON('/api/runs')).items })

function fmtHour(v) {
  return v === null || v === undefined ? '—' : hourToTime(v)
}

async function openDetail(r) {
  err.value = ''
  try {
    selected.value = await getJSON(`/api/runs/${r.id}`)
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <p class="hint">损耗与片数为当时快照，修改加耗或停用班次不会重算旧记录。</p>
    <table class="tbl">
      <thead><tr><th>时间</th><th>房间</th><th>砖型</th><th>施工钟点</th><th>总损耗</th><th>片数</th><th></th></tr></thead>
      <tbody>
        <tr v-for="r in items" :key="r.id">
          <td>{{ r.created_at?.slice(0, 19) }}</td>
          <td>{{ r.room_name }}</td>
          <td>{{ r.tile_name }}</td>
          <td>{{ fmtHour(r.work_time) }}</td>
          <td>{{ r.waste_pct }}%<span v-if="r.surcharge_pct" class="surcharge-tag">（含班次 {{ r.surcharge_pct }}%）</span></td>
          <td>{{ r.result?.order_count }}</td>
          <td><button @click="openDetail(r)">详情</button></td>
        </tr>
      </tbody>
    </table>

    <div v-if="selected" class="run-detail">
      <h2>记录 #{{ selected.id }} 详情（快照）</h2>
      <ul>
        <li>房间：{{ selected.room_name }} / 砖型：{{ selected.tile_name }}</li>
        <li>下单片数：<strong>{{ selected.result?.order_count }}</strong>，净用量 {{ selected.result?.raw_count }} 片</li>
        <li>实际采用总损耗：<strong>{{ selected.waste_pct }}%</strong>
          <span v-if="selected.surcharge_pct">（基础 {{ selected.base_waste_pct }}% + {{ selected.shift_name }} 加耗 {{ selected.surcharge_pct }}%）</span>
        </li>
        <li>施工钟点：{{ fmtHour(selected.work_time) }}</li>
        <li>备注：{{ selected.note || '—' }}</li>
      </ul>
      <button @click="selected = null">关闭</button>
    </div>
    <p v-if="err" class="alert">{{ err }}</p>
  </div>
</template>
