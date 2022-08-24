<template>
  <v-app>

    <v-main class="pt-3 mt-5">
      <!-- Provides the application the proper gutter -->
     <router-view></router-view>
    </v-main>
    <Snackbar />
  </v-app>
</template>

<script>
import Snackbar from "./components/notifier/Notifier.vue";

export default {
  components: {
    Snackbar,
  }
};
</script>

<style>
</style>