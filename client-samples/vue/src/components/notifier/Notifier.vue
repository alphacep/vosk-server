<template>
  <div name="snackbars">
    <v-snackbar v-model="show" :color="color" :timeout="timeout" :top="'top'" left="left">
      {{ text }}

      <template v-slot:action="{ attrs }">
        <v-btn dark text v-bind="attrs" @click="show = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  created() {
    this.$store.subscribe((mutation, state) => {
      if (mutation.type === "SHOW_MESSAGE") {
        this.text = state.Snackbar.text;
        this.color = state.Snackbar.color;
        this.timeout = state.Snackbar.timeout;
        this.show = true;
      }
    });
  },
  data() {
    return {
      show: false,
      color: "",
      text: "",
      timeout: -1,
    };
  },
};
</script>