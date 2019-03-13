<template>
  <div class="hello">
    <h1>{{ msg }}</h1>

    <ul>
        <li v-for="(node, index) in nodes" :key="node.id">
          {{ index }} - {{ node.name }}
        </li>
    </ul>
  </div>
</template>

<script>
import ApiRoutes from '../api/ApiRoutes'

export default {
  name: 'Home',
  data () {
    return {
      msg: 'Welcome to Yukon',
      nodes: [],
      error: '',
    }
  },
  mounted () {
    axios
      .get(ApiRoutes.Nodes.GetAll)
      .then(response => (this.nodes = response.data))
      .catch(error => console.log(error))
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: blue;
}
</style>
