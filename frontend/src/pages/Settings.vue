<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const settings = ref({})
const stripLen = ref('')
const msg = ref('')
const err = ref('')
onMounted(async () => {
  settings.value = await getJSON('/api/settings')
  stripLen.value = settings.value.skirting_strip_len
})
async function saveStripLen() {
  msg.value = ''
  err.value = ''
  if (!(Number(stripLen.value) > 0)) {
    err.value = '默认条长必须大于 0'
    return
  }
  try {
    await putJSON('/api/settings/skirting_strip_len', { value: String(stripLen.value) })
    settings.value = await getJSON('/api/settings')
    msg.value = '已保存（仅影响新测算，历史记录不变）'
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>参数</h1>
    <ul>
      <li v-for="(v, k) in settings" :key="k">{{ k }}：{{ v }}</li>
    </ul>
    <h2>收边条默认单根条长</h2>
    <label>条长 <input v-model="stripLen" type="number" min="0" step="0.1" /> m</label>
    <button @click="saveStripLen">保存</button>
    <p v-if="msg">{{ msg }}</p>
    <p v-if="err" class="alert">{{ err }}</p>
  </div>
</template>
