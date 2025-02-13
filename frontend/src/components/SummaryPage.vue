<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const summaries = ref([])
const apiUrl = 'http://localhost:5000/summary'
const dataReady = ref(false)

onMounted(() => {
  axios
    .get(apiUrl)
    .then(function (response) {
      summaries.value = response.data
      dataReady.value = true
    })
    .catch(function (error) {
      console.log(error)
    })
    .finally(function () {
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
          <td>
            <RouterLink :to="{ name: 'agency', params: { agencyName: agency.name } }">{{
              agency.name
            }}</RouterLink>
          </td>
          <td>{{ agency.short_name }}</td>
          <td>{{ agency.new_word_count }}</td>
          <td>{{ agency.old_word_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
