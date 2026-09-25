<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const openId = ref(null)
const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function toggle(id) {
  if (openId.value === id) { openId.value = null; detail.value = null; return }
  openId.value = id
  detail.value = await getJSON(`/api/runs/${id}`)
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead><tr><th>时间</th><th>房间</th><th>砖型</th><th>片数</th><th>收边条</th><th></th></tr></thead>
      <tbody>
        <template v-for="r in items" :key="r.id">
          <tr>
            <td>{{ r.created_at?.slice(0, 19) }}</td>
            <td>{{ r.room_name }}</td>
            <td>{{ r.tile_name }}</td>
            <td>{{ r.result?.order_count }}</td>
            <td>
              <template v-if="r.result?.skirting">
                {{ r.result.skirting.linear_m }} 延米 / {{ r.result.skirting.strips }} 根（单根 {{ r.result.skirting.strip_len }} m）
              </template>
              <template v-else>—</template>
            </td>
            <td><button class="link-btn" @click="toggle(r.id)">{{ openId === r.id ? '收起' : '打开' }}</button></td>
          </tr>
          <tr v-if="openId === r.id && detail" class="run-detail">
            <td colspan="6">
              <template v-if="detail.result?.skirting">
                打开后：{{ detail.result.skirting.linear_m }} 延米 /
                {{ detail.result.skirting.strips }} 根（单根 {{ detail.result.skirting.strip_len }} m）
              </template>
              <template v-else>无收边条</template>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
