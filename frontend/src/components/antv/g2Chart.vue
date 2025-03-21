<template>
    <div ref="container"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { Chart } from '@antv/g2'
import { useConfig } from '/@/stores/config'

const config = useConfig()

const props = defineProps(['options'])

const container = ref(null)
let chart = null

// 渲染
function renderChart(container) {
    chart = new Chart({
        container: container,
        theme: config.layout.isDark ? 'classicDark' : 'light',
    })

    chart.options(props.options)

    // 渲染可视化
    chart.render()

    return chart
}

onMounted(() => {
    renderChart(container.value)
})

watch(
    () => props.options,
    (newVal) => {
        chart.options(newVal)
        chart.render()
    }
)

watch(
    () => config.layout.isDark,
    (newVal) => {
        chart.theme({ type: newVal ? 'classicDark' : 'light' })
        chart.render()
    }
)
</script>
