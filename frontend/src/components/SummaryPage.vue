<script setup>
import { ref, onMounted, useTemplateRef, watch } from 'vue'
import axios from 'axios'

const summaries = ref([])
const agencyRef = useTemplateRef('agencies')
const apiUrl = 'http://localhost:5000/summary'
const dataReady = ref(false)
const reachedThen = ref(false)

onMounted(() => {
  axios
    .get(apiUrl)
    .then(function (response) {
      summaries.value = response.data
      reachedThen.value = true
      console.log('finished then()')
    })
    .catch(function (error) {
      console.log(error)
    })
    .finally(function () {
      dataReady.value = true
    })
})
</script>

<template>
  <div>
    <h1>Regulation Summary by Agency</h1>
    <table>
      <thead>
        <tr>
          <th>Agency</th>
          <th>Short name</th>
          <th>2024-02-01 regulation word count</th>
          <th>2018-02-01 regulation word count</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="agency in summaries" :key="agency.result_id" v-if="dataReady">
          <td>{{ agency.name }}</td>
          <td>{{ agency.short_name }}</td>
          <td>{{ agency.new_word_count }}</td>
          <td>{{ agency.old_word_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
