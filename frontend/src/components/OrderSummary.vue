<script setup>
defineProps({
  result: { type: Object, default: null },
})
const edgeLabel = (e) => ({ length: '长边', width: '宽边' }[e] ?? e)
</script>
<template>
  <div v-if="result" class="order-summary">
    <div class="hero">{{ result.order_count }} 片</div>
    <ul>
      <li>净用量 {{ result.raw_count }} 片，损耗 {{ result.waste_pct }}%</li>
      <li>地面 {{ result.area_m2 }} m²，单砖 {{ result.piece_m2 }} m²</li>
      <li v-if="result.skirting">
        收边条（{{ edgeLabel(result.skirting.edge) }}交界）：{{ result.skirting.linear_m }} 延米，
        {{ result.skirting.strips }} 根（单根 {{ result.skirting.strip_len }} m）
      </li>
    </ul>
  </div>
</template>
