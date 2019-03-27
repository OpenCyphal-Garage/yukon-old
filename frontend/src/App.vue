<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div id="navBar">
      <a class="ml-2" @click="goHome" ref="homeButton">Home</a>
      <a class="ml-3" @click="goBack" ref="backButton">Back</a>
      <a class="ml-3" @click="goRegisterView" ref="globalRegisterViewButton">Global Register View</a>

    </div>
    <div id="app" class="container">
    <router-view/>
    </div>
  </div>
</template>

<script>
import AppRoutes from './router'
export default {
  name: 'App',
  methods: {
    goBack () {
      this.$router.back()
    },
    goHome () {
      this.$router.push(AppRoutes.Home)
    },
    goRegisterView () {
      this.$router.push(AppRoutes.GlobalRegisterView)
    }
  }
}
</script>

<style>
  @import './assets/styles/core.css';
  @import './assets/styles/nodeStatus.css';

  #navBar {
    width: 100%;
    background-color: #6c757d;
  }

  #navBar > a {
    font-size: 24px;
    color: white;
  }

  #navBar > a:hover {
    cursor: pointer;
    text-decoration: underline;
  }
</style>
