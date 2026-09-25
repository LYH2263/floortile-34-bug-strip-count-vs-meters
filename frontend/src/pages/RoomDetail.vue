<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const room = ref(null)
const latestRun = ref(null)
const edgeLabel = (e) => ({ length: '长边', width: '宽边' }[e] ?? e)
onMounted(async () => {
  room.value = await getJSON(`/api/rooms/${props.id}`)
  const runs = (await getJSON(`/api/runs?room_id=${props.id}`)).items
  latestRun.value = runs.find(r => r.result?.skirting) || null
})
</script>
<template>
  <div class="page" v-if="room">
    <h1>{{ room.name }}</h1>
    <div v-if="room.data_quality === 'dirty'" class="alert">该房间尺寸异常：{{ room.note }}</div>
    <dl>
      <dt>长度</dt><dd>{{ room.length }} m</dd>
      <dt>宽度</dt><dd>{{ room.width }} m</dd>
      <dt>面积</dt><dd>{{ (room.length * room.width).toFixed(2) }} m²</dd>
    </dl>
    <template v-if="latestRun">
      <h2>收边条（最近测算）</h2>
      <dl>
        <dt>交界边</dt><dd>{{ edgeLabel(latestRun.result.skirting.edge) }}</dd>
        <dt>延米</dt><dd>{{ latestRun.result.skirting.linear_m }} m</dd>
        <dt>根数</dt><dd>{{ latestRun.result.skirting.strips }} 根</dd>
        <dt>单根条长</dt><dd>{{ latestRun.result.skirting.strip_len }} m</dd>
        <dt>测算时间</dt><dd>{{ latestRun.created_at?.slice(0, 19) }}</dd>
      </dl>
    </template>
    <router-link to="/bench">去测算</router-link>
  </div>
</template>
