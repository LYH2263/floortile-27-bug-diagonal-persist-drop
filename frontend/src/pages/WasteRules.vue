<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const settings = ref({})
const factor = ref(1.1)
const msg = ref('')
const err = ref('')

async function load() {
  settings.value = await getJSON('/api/settings')
  factor.value = settings.value.diag_factor ?? 1.1
}
onMounted(load)

async function saveFactor() {
  msg.value = ''
  err.value = ''
  try {
    const r = await putJSON('/api/settings/diag-factor', { diag_factor: Number(factor.value) })
    factor.value = r.diag_factor
    msg.value = `默认斜铺系数已更新为 ${r.diag_factor}`
    await load()
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>损耗规则</h1>
    <p>默认损耗率按面积法向上取整后再乘 (1+损耗%)。</p>
    <p>当前默认损耗：<strong>{{ settings.waste_pct }}%</strong></p>

    <h2>斜铺默认系数</h2>
    <p>启用斜铺时按「房间面积 × 斜向折算系数」放大后向上取整得到斜铺净用量，再套当前损耗得出斜铺订货片数。</p>
    <label>默认斜向折算系数
      <input type="number" v-model.number="factor" step="0.01" min="0.01" max="2" />
      <span class="hint">（须大于 0，上限 2）</span>
    </label>
    <button @click="saveFactor">保存默认系数</button>
    <p v-if="msg" class="ok">{{ msg }}</p>
    <p v-if="err" class="alert">{{ err }}</p>
    <p class="hint">修改默认系数只影响之后的新测算；已保存的历史 run 保留写入时的系数与片数，不会重算。</p>

    <p>网格预览块数可能大于面积法片数，下单以面积法 order_count 为准。</p>
  </div>
</template>
