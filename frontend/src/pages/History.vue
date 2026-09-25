<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const openId = ref(null)
const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function toggle(id) {
  if (openId.value === id) {
    openId.value = null
    detail.value = null
    return
  }
  openId.value = id
  detail.value = await getJSON(`/api/runs/${id}`)
}
function listDiag(r) {
  if (!r.result?.diagonal) return '—'
  return r.result?.diag_order_count ?? '—'
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead><tr><th>编号</th><th>时间</th><th>房间</th><th>砖型</th><th>正铺片数</th><th>斜铺片数</th><th>系数</th><th></th></tr></thead>
      <tbody>
        <template v-for="r in items" :key="r.id">
          <tr>
            <td>{{ r.id }}</td>
            <td>{{ r.created_at?.slice(0, 19) }}</td>
            <td>{{ r.room_name }}</td>
            <td>{{ r.tile_name }}</td>
            <td>{{ r.result?.order_count }}</td>
            <td>{{ listDiag(r) }}</td>
            <td>{{ r.result?.diagonal ? '×' + r.result?.diag_factor : '—' }}</td>
            <td><button class="link-btn" @click="toggle(r.id)">{{ openId === r.id ? '收起' : '打开' }}</button></td>
          </tr>
          <tr v-if="openId === r.id && detail" class="run-detail">
            <td colspan="8">
              开关 {{ detail.result?.diagonal ? '开' : '关' }}，
              正铺 {{ detail.result?.order_count }}，
              斜铺 {{ detail.result?.diagonal ? detail.result?.diag_order_count : '—' }}，
              系数 {{ detail.result?.diagonal ? ('×' + detail.result?.diag_factor) : '—' }}
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <p class="hint">列表摘要与按号打开详情分别读取列表/详情接口。</p>
  </div>
</template>
