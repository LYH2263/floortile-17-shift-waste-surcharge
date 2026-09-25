<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead>
        <tr><th>时间</th><th>房间</th><th>砖型</th><th>片数</th><th>总损耗</th><th>施工钟点</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="r in items" :key="r.id">
          <td>{{ r.created_at?.slice(0, 19) }}</td>
          <td>{{ r.room_name }}</td>
          <td>{{ r.tile_name }}</td>
          <td>{{ r.result?.order_count }}</td>
          <td>{{ r.waste_pct }}%</td>
          <td>{{ r.construction_hour !== null && r.construction_hour !== undefined ? r.construction_hour + ' 时' : '—' }}</td>
          <td><router-link :to="`/history/${r.id}`">详情</router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
