<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import OrderSummary from '../components/OrderSummary.vue'
import TileGridPreview from '../components/TileGridPreview.vue'

const rooms = ref([])
const tiles = ref([])
const roomId = ref(1)
const tileId = ref(1)
const result = ref(null)
const err = ref('')
const diagonal = ref(false)
const diagFactor = ref(1.1)

function calcParams() {
  const p = { room_id: roomId.value, tile_id: tileId.value }
  if (diagonal.value) {
    p.diagonal = true
    p.diag_factor = Number(diagFactor.value)
  }
  return p
}

onMounted(async () => {
  rooms.value = (await getJSON('/api/rooms')).items.filter(r => r.data_quality === 'clean')
  tiles.value = (await getJSON('/api/tiles')).items.filter(t => t.data_quality === 'clean')
  const settings = await getJSON('/api/settings')
  diagFactor.value = settings.diag_factor ?? 1.1
  if (rooms.value.length) roomId.value = rooms.value[0].id
  if (tiles.value.length) tileId.value = tiles.value[0].id
})

async function preview() {
  err.value = ''
  try {
    const qs = new URLSearchParams(calcParams()).toString()
    result.value = await getJSON(`/api/estimate?${qs}`)
  } catch (e) {
    err.value = e.message
    result.value = null
  }
}

async function saveRun() {
  err.value = ''
  try {
    result.value = await postJSON('/api/estimate', {
      ...calcParams(),
      save: true,
      note: '前端保存',
    })
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>下单测算</h1>
    <label>房间 <select v-model.number="roomId"><option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option></select></label>
    <label>砖型 <select v-model.number="tileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
    <label class="inline">
      <input type="checkbox" v-model="diagonal" />
      启用斜铺（45° 对角）
    </label>
    <label v-if="diagonal">
      斜向折算系数
      <input type="number" v-model.number="diagFactor" step="0.01" min="0.01" max="2" />
      <span class="hint">面积 × 系数后向上取整，再套当前损耗</span>
    </label>
    <button @click="preview">试算</button>
    <button @click="saveRun">保存记录</button>
    <p v-if="err" class="alert">{{ err }}</p>
    <OrderSummary :result="result" />
    <TileGridPreview v-if="result?.layout" :cols="result.layout.cols" :rows="result.layout.rows" :grid-count="result.layout.grid_count" />
  </div>
</template>
