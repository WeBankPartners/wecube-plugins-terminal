<template>
  <div>
    <!-- <div class="header">
      <Header />
    </div> -->
    <section>
      <Tabs :value="activeTab" @on-click="changeTab">
        <template v-for="(tabItem, tabIndex) in tabs">
          <TabPane :label="$t(tabItem.label)" :name="tabItem.path" :key="tabIndex"> </TabPane>
        </template>
      </Tabs>
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
// import Header from './components/header'
export default {
  name: '',
  data () {
    return {
      activeTab: '/terminal/terminalAuthorization/sessionRecords',
      tabs: [
        { label: 't_session_records', path: '/terminal/terminalAuthorization/sessionRecords' },
        { label: 't_transfer_records', path: '/terminal/terminalAuthorization/transferRecords' },
        { label: 't_permissions', path: '/terminal/terminalAuthorization/permissions' }
      ]
    }
  },
  mounted () {
    this.activeTab = this.$route.path
  },
  methods: {
    changeTab (path) {
      this.activeTab = path
      if (this.$route.path === path) return
      this.$router.push({ path: path })
    }
  },
  components: {
    // Header
  }
}
</script>

<style lang="scss" scoped>
.content-container {
  height: calc(100% - 50px);
  padding: 5px 30px;
}
</style>
