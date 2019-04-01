<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
  <div>
    <b-navbar>
      <b-navbar-brand href="#" @click="goHome">
         <img src="./assets/logo.svg" alt="Home" style="width: 100px;">
      </b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

        <b-navbar-nav>
          <b-nav-item @click="goBack" class="mr-4">Back</b-nav-item>

          <b-nav-item v-for="route in navigationRouteOptions"
            v-bind:key="route.name"
            @click="goTo(route.path)">{{ route.name }}</b-nav-item>
        </b-navbar-nav>

        <div class="navbar-nav ml-auto">
          <b-nav-item-dropdown text="Useful Links" right>
            <b-dropdown-item href="https://new.uavcan.org/">UAVCAN</b-dropdown-item>
            <b-dropdown-item href="https://new.uavcan.org/specification">Specification</b-dropdown-item>
            <b-dropdown-item href="https://forum.uavcan.org/">Forums</b-dropdown-item>
            <b-dropdown-item href="https://github.com/UAVCAN">Github</b-dropdown-item>
          </b-nav-item-dropdown>
        </div>
    </b-navbar>
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
  data () {
    return {
      navigationRouteOptions: [AppRoutes.Home, AppRoutes.GlobalRegisterView, AppRoutes.Plotter]
    }
  },
  methods: {
    goBack () {
      this.$router.back()
    },
    goHome () {
      this.$router.push(AppRoutes.Home)
    },
    goTo (routeName) {
      this.$router.push(routeName)
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
