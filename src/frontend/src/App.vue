<template>
  <div id="app">
    <Header />
    <router-view></router-view>
    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import ImageUploadView from './components/ImageUploadView.vue';
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';

export default defineComponent({
  name: 'App',
  components: {
    Header,
    Footer
  },
  setup() {
    const router = useRouter();
    router.push({ name: 'ImageUpload' });
    return {};
  }
});
</script>
