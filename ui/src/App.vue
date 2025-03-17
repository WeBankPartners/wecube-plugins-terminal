<template>
  <div id="app">
    <div v-if="showMenus" class="header">
      <Header @allMenus="allMenus" />
    </div>
    <div class="app-content-container">
      <BackTop :height="100" :bottom="100" />
      <router-view />
    </div>
  </div>
</template>
<script>
import Header from '@/pages/components/header'
export default {
  components: { Header },
  data () {
    return {
      showMenus: true,
      isShowBreadcrum: true,
      allMenusAry: [],
      parentBreadcrumb: '',
      childBreadcrumb: '',
      allMenus: []
    }
  },
  watch: {
    $route (to) {
      if (to.path === '/login') {
        this.showMenus = false
      } else {
        this.showMenus = true
      }
    }
  },
  methods: {},
  mounted () {}
}
</script>
<style lang="scss">
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
  min-width: 1280px;

  .app-content-container {
    // height: 100%;
  }
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
.ivu-layout,
.ivu-layout-sider {
  height: 100%;
}
.spin-icon-load {
  animation: ani-demo-spin 1s linear infinite;
}
body {
  height: 100%;
  overflow: auto !important;
}
html {
  height: 100%;
}
.ivu-table-fixed-body {
  height: auto !important;
}
</style>
