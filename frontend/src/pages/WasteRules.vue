<script setup>
import { onMounted, reactive, ref } from 'vue'
import { deleteJSON, getJSON, hourToTime, postJSON, putJSON, timeToHour } from '../api'

const settings = ref({})
const shifts = ref([])
const err = ref('')
const form = reactive({ name: '', start: '22:00', end: '06:00', surcharge: 5 })

async function loadAll() {
  settings.value = await getJSON('/api/settings')
  shifts.value = (await getJSON('/api/shifts')).items
}
onMounted(loadAll)

async function submit() {
  err.value = ''
  try {
    await postJSON('/api/shifts', {
      name: form.name,
      start_hour: timeToHour(form.start),
      end_hour: timeToHour(form.end),
      surcharge_pct: Number(form.surcharge),
    })
    form.name = ''
    await loadAll()
  } catch (e) {
    err.value = e.message
  }
}

async function toggleActive(s) {
  err.value = ''
  try {
    await putJSON(`/api/shifts/${s.id}`, { active: !s.active })
    await loadAll()
  } catch (e) {
    err.value = e.message
  }
}

async function remove(s) {
  err.value = ''
  try {
    await deleteJSON(`/api/shifts/${s.id}`)
    await loadAll()
  } catch (e) {
    err.value = e.message
  }
}

function describe(s) {
  const wrap = s.start_hour > s.end_hour ? '（跨午夜）' : ''
  return `${hourToTime(s.start_hour)} – ${hourToTime(s.end_hour)}${wrap}`
}
</script>
<template>
  <div class="page">
    <h1>损耗规则</h1>
    <p>默认损耗率按面积法向上取整后再乘 (1+损耗%)，当前默认损耗：<strong>{{ settings.waste_pct }}%</strong>。</p>
    <p>命中启用中的班次时，在基础损耗上再加一段加耗百分点后再算 order；班次停用后新测不再加耗，旧记录保留当时数值。</p>

    <h2>班次加耗</h2>
    <table class="tbl">
      <thead><tr><th>班次</th><th>钟点窗</th><th>加耗</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="s in shifts" :key="s.id" :class="{ 'shift-off': !s.active }">
          <td>{{ s.name }}</td>
          <td>{{ describe(s) }}</td>
          <td>+{{ s.surcharge_pct }}%</td>
          <td>{{ s.active ? '启用' : '已停用' }}</td>
          <td>
            <button @click="toggleActive(s)">{{ s.active ? '停用' : '启用' }}</button>
            <button @click="remove(s)">删除</button>
          </td>
        </tr>
        <tr v-if="!shifts.length"><td colspan="5">尚未配置班次</td></tr>
      </tbody>
    </table>

    <h3>新增班次</h3>
    <form class="shift-form" @submit.prevent="submit">
      <label>名称 <input v-model="form.name" required placeholder="夜班" /></label>
      <label>起始 <input v-model="form.start" type="time" required /></label>
      <label>结束 <input v-model="form.end" type="time" required /></label>
      <label>加耗% <input v-model="form.surcharge" type="number" step="0.5" min="0" required /></label>
      <button type="submit">保存班次</button>
    </form>
    <p v-if="err" class="alert">保存失败：{{ err }}</p>
    <p class="hint">起始与结束相同、钟点越界或加耗为负时保存失败；结束早于起始表示跨午夜窗。</p>
  </div>
</template>
