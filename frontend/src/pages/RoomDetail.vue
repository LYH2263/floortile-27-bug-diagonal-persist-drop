<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const room = ref(null)
const tiles = ref([])
const tileId = ref(null)
const diagonal = ref(false)
const diagFactor = ref(1.1)
const result = ref(null)
const err = ref('')

onMounted(async () => {
  room.value = await getJSON(`/api/rooms/${props.id}`)
  tiles.value = (await getJSON('/api/tiles')).items.filter(t => t.data_quality === 'clean')
  const settings = await getJSON('/api/settings')
  diagFactor.value = settings.diag_factor ?? 1.1
  if (tiles.value.length) tileId.value = tiles.value[0].id
})

async function preview() {
  err.value = ''
  result.value = null
  try {
    const p = { room_id: props.id, tile_id: tileId.value }
    if (diagonal.value) { p.diagonal = true; p.diag_factor = Number(diagFactor.value) }
    const qs = new URLSearchParams(p).toString()
    result.value = await getJSON(`/api/estimate?${qs}`)
  } catch (e) {
    err.value = e.message
  }
}
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

    <template v-if="room.data_quality !== 'dirty'">
      <label>砖型
        <select v-model.number="tileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select>
      </label>
      <label class="inline"><input type="checkbox" v-model="diagonal" /> 启用斜铺（45° 对角）</label>
      <label v-if="diagonal">斜向折算系数
        <input type="number" v-model.number="diagFactor" step="0.01" min="0.01" max="2" />
      </label>
      <button @click="preview">试算</button>
      <p v-if="err" class="alert">{{ err }}</p>
      <div v-if="result" class="dual-count">
        <div>正铺订货 <strong>{{ result.order_count }}</strong> 片</div>
        <div v-if="result.diagonal">斜铺订货 <strong>{{ result.diag_order_count }}</strong> 片
          <span class="hint">（净用量 {{ result.diag_raw_count }}，系数 ×{{ result.diag_factor }}）</span>
        </div>
      </div>
    </template>
    <router-link to="/bench">去下单台</router-link>
  </div>
</template>
