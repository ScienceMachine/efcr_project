<template>
  <div>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'

ChartJS.register(Title, Tooltip, LineElement, CategoryScale, LinearScale, PointElement)

const props = defineProps({
  xValues: {
    type: Array,
    required: true
  },
  yValues: {
    type: Array,
    required: true
  }
})

const chartData = computed(() => ({
  labels: props.xValues,
  datasets: [
    {
      label: 'Data',
      backgroundColor: '#f87979',
      data: props.yValues
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
}
</script>
