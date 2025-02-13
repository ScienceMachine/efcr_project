<script setup>
import axios from 'axios'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import LineChart from './LineChart.vue'

const route = useRoute()

const props = defineProps({
  agencyName: String,
})
const apiUrl = 'http://localhost:5000/agency_details'
const agencyFeatures = ref({})
const dataReady = ref(false)

const xVals = ref([])
const yVals = ref([])

watch(() => route.params.agencyName, fetchData, { immediate: true })

function fetchData() {
  axios
    .post(apiUrl, { agency_name: route.params.agencyName })
    .then(function (response) {
      agencyFeatures.value = response.data
      dataReady.value = true
      for (const item of response.data.features) {
        xVals.value.push(item.date)
        yVals.value.push(item.word_count)
      }
    })
    .catch(function (error) {
      console.log(error)
    })
    .finally(function () {})
}
</script>

<template>
  <RouterLink :to="{ path: '/' }">Home</RouterLink>
  <h1>Agency Summary</h1>
  <h2>{{ agencyName }}</h2>
  <h3>Regulation word count</h3>
  <div v-if="dataReady">
    <LineChart :xValues="xVals" :yValues="yVals" />
  </div>
</template>
