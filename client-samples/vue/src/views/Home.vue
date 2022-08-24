<template>
  <v-container>
    <v-card-title class="justify-center font-weight-bold"
      >Arabic (Egyptian) language</v-card-title
    >
    <div v-if="socketStatus == 'start'" class="text-center mb-3">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            @click="switchSpokenLang"
            class="mx-1"
            dark
            large
            color="error"
            >ابدء</v-btn
          >
        </template>
        <span>سوف يمسح النص ويمكنك البدء من جديد</span>
      </v-tooltip>
    </div>

    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      value="15"
    ></v-progress-linear>
    <v-textarea
      ref="printedTextContainer"
      id="textcontainer"
      rows="8"
      row-height="40"
      :readonly="isReadOnly"
      name="input-7-1"
      filled
      label="سيظهر النص الخاص بك هنا..."
      v-model="printedText"
    ></v-textarea>

    <div v-if="socketStatus != 'start'" class="text-center">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            @click="enOfFile"
            class="mx-1"
            dark
            large
            color="error"
            >“قف”</v-btn
          >
        </template>
        <span>سوف يمسح النص ويمكنك البدء من جديد</span>
      </v-tooltip>
      <v-btn
        v-if="socketStatus == 'listening'"
        @click="pauseRecording"
        class="mx-1"
        dark
        large
        >“إيقاف مؤقت”</v-btn
      >

      <v-btn
        v-if="socketStatus == 'pause'"
        @click="continueRecording"
        class="mx-1"
        dark
        large
        >“متابعة”</v-btn
      >
    </div>
    <div class="text-center">
      <v-btn
        v-if="socketStatus == 'start' && isSocketInit && sessionIdIsNull()"
        @click="saveModifiedData"
        class="mx-1"
        dark
        large
        >“حفظ”</v-btn
      >
    </div>

    <!-- SNACK BAR -->

    <v-snackbar
      :color="snackbarcontent.color"
      top
      v-model="snackbarcontent.snackbar"
      :timeout="timeout"
    >
      {{ snackbarcontent.text }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbarcontent.snackbar = false"
          >Close</v-btn
        >
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import dictateService from "../services/dictate-service";
import EndPoints from "../services/endpoint";

export default {
  data: () => ({
    spokenLang: "egyptian",
    partialText: "",
    printedText: "",
    loading: false,
    socketStatus: "start",

    timeout: 2000,
    isReadOnly: true,
    isSocketInit: false,
    snackbarcontent: {
      text: "",
      snackbar: false,
      color: "error",
    },
  }),
  mounted() {
    // console.log(process.env.VUE_APP_ENV_VARIABLE);
    this.$vuetify.rtl = true;
  },
  methods: {
    saveModifiedData() {
      const x = {
        session_id: localStorage.getItem("session_id"),
        text: this.printedText,
      };
      dictateService.saveModifiedData(x).then((res) => {
        this.snackbarcontent.text = res.message;
        this.snackbarcontent.snackbar = true;
        this.snackbarcontent.color = "success";
      });
    },
    switchSpeechRecognition(environment) {
      localStorage.removeItem("session_id"); // remove old session_id when starting new session
      this.isReadOnly = true;
      this.loading = true;
      this.socketStatus = "listening";
      this.printedText = "";
      this.partialText = "";

      if (!dictateService.isInitialized()) {
        this.isSocketInit = true;
        this.printedText = "";

        // console.log('dictateService.isInitialized()',dictateService.isInitialized());

        dictateService.init({
          server: environment,

          onResults: (hyp) => {
            this.loading = false;

            // this.partialText = this.partialText.replace( "<موسيقى>" || '<music>', "🎶") + hyp.text.replace( "<موسيقى>" || '<music>', "🎶") + '\n';

            // this.printedText = this.partialText.replace( "<موسيقى>" || '<music>', "🎶");
            // console.log(this.partialText, 'onResults');
            if (hyp.partial == "False") {
              // console.log(hyp.partial);
              this.partialText =
                this.partialText.replace("<music>", "🎶") +
                hyp.text.replace("<music>", "🎶") +
                "\n";

              this.printedText = this.partialText.replace("<music>", "🎶");
            } else if (hyp.partial == "True") {
              // console.log(hyp.partial);
            }

            if (dictateService.isEndOfFile && hyp.partial == "False") {
              this.stopRecording();
            }
            // this.printedTextContainer.nativeElement.scrollTop = this.printedTextContainer.nativeElement.scrollHeight;
          },
          onPartialResults: (hyp) => {
            // this.loading = false
            if (hyp.partial == "False") {
              // console.log(hyp.partial);
            } else if (hyp.partial == "True") {
              // console.log(hyp.partial);
              this.printedText =
                this.partialText.replace("<music>", "🎶") +
                hyp.text
                  .replace("<music>", "🎶")
                  .replace("False", "")
                  .replace("True", "");
            }

            // this.printedText += this.replaceTags(hyp).trim() + ' ';

            if (dictateService.isEndOfFile && hyp.partial == "False") {
              this.stopRecording();
            }
            // console.log(this.printedText, 'onPartialResults');
          },
          onError: (code, data) => {
            if (code == 2) {
              this.loading = false;
            }
            // console.log(code, data);
            this.snackbarcontent.text = data;
            this.snackbarcontent.snackbar = true;
            this.snackbarcontent.color = "error";
            this.stopRecording();
          },
          onEvent: (code, data) => {
            // console.log(code, data);
            // this.printedText += data.partial ?data.partial + ' ' :'  '
            // console.log(this.printedText);
          },
        });
        this.socketStatus = "listening";

        // this.buttonText = 'Stop Recognition';
      } else if (dictateService.isRunning()) {
        this.isSocketInit = true;
        // console.log('dictateService.isRunning()',dictateService.isRunning());
        dictateService.resume();
        this.socketStatus = "listening";

        // this.buttonText = 'Stop Recognition';
      } else {
        // console.log('else');
        dictateService.pause();
        this.socketStatus = "pause";

        // this.buttonText = 'Start Recognition';
      }
    },
    enOfFile() {
      if (this.sessionIdIsNull()) {
        dictateService.endOfFile();
      }
    },

    // This method check if session_id is null or not
    sessionIdIsNull() {
      if (dictateService.session_id) {
        return true;
      } else {
        return false;
      }
    },

    switchSpokenLang() {
      this.stopRecording();

      if (this.spokenLang === "egyptian") {
        this.switchSpeechRecognition(EndPoints.SOCKET_BASE_URL);
      }
    },

    stopRecording() {
      // console.log('stop');
      dictateService.cancel();

      this.socketStatus = "start";
      this.isReadOnly = false;
      this.loading = false;
      // this.spokenLang=''
    },

    pauseRecording() {
      dictateService.pause();
      this.socketStatus = "pause";
    },

    continueRecording() {
      if (dictateService.isRunning()) {
        dictateService.resume();
        this.socketStatus = "listening";
      }
    },
  },
};
</script>

<style>
</style>
