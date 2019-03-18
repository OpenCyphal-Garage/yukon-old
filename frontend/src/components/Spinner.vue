<template>
  <div id="app">
     <fingerprint-spinner
          :animation-duration="1500"
          :size="60"
          :color="'#3366ff'"
     />
  </div>
</template>

<script>
import {FingerprintSpinner} from 'epic-spinners'
export default {
  name: 'Spinner',
  components: {
    FingerprintSpinner
  }
}
</script>

<style>

</style>
