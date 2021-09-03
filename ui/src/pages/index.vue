<template>
  <div>
    <!-- <div class="header">
      <Header @allMenus="allMenus" />
    </div> -->
    <div>
      <transition name="fade" mode="out-in">
        <router-view class="pages"></router-view>
      </transition>
    </div>
  </div>
</template>

<script>
import Header from '@/pages/components/header'
export default {
  components: { Header },
  data () {
    return {
      isShowBreadcrum: true,
      allMenusAry: [],
      parentBreadcrumb: '',
      childBreadcrumb: '',
      allMenus: []
    }
  },
  methods: {},
  mounted () {}
}
</script>

<style lang="scss" scoped>
.header {
  width: 100%;
  background-color: #515a6e;
  display: block;
}
.content-container {
  height: calc(100% - 50px);
  padding: 5px 30px;
}

.ivu-breadcrumb {
  color: #515a6e;
}
</style>
