<template>
  <div>
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
export default {
  name: '',
  data () {
    return {
      activeTab: '/terminalManagement/hosts',
      tabs: [
        { label: 'asset', path: '/terminalManagement/hosts' },
        { label: 'jump_server', path: '/terminalManagement/jumpServer' }
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
  }
}
</script>

<style lang="scss" scoped>
.content-container {
  height: calc(100% - 50px);
  padding: 5px 30px;
}
</style>
