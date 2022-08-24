<!-- HOW TO SET UP FRONTEND ENV -->

# BREIF

### **This is speach-to-text application**

**1-INSTALL NODE JS RECOMMENDED FOR MOST USERS**
DOWNLOAD https://nodejs.org/en/

**2-INSTALL VUE & VUE CLI**
RUN `npm install -g @vue/cli` ## IN TERMINAL OR POWERSHELL
RUN `npm install vue` ## IN TERMINAL OR POWERSHELL

**3-CLONE THE PROJECT FROM GITLAB**

### IF YOU DON'T USE GIT AT ALL YOU NEED TO INSTALL GIT TO CLONE THE PROJECT

https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

### AFTER SETUP GIT YOU NEED TO CLONE THE PROJECT

RUN `git clone https://gitlab.com/nada_azzam/live-transcribe-vue`
RUN `npm install` ## INSIDE OUR FOLDER RUN THIS COMMAND
Run `npm run serve` for a dev server. Navigate to `http://localhost:8080/`. The app will automatically reload if you change any of the source files.

## BUILD PROJECT FOR DEPLOYING

RUN `npm run build --prod`

## TO CUSTOMZIE ANYTHING INSIDE YOUR PROJECT
### TO CUSTOMIZE ICONS

GO TO `https://mui.com/components/material-icons/`

### TO CHANGE COLORS GLOBAl

GO TO `live-transcribe-vue/src/assets/scss/main.scss`

## TO CUSTOMIZE HOME HTML

GO TO `live-transcribe-vue/src/views/Home.vue`

## HOW TO INTEGRATE WITH BACKEND OR ENGINE

### YOU HAVE TWO FILES

- `live-transcribe-vue/src/services/dictate-service.js`
  - const INTERVAL = 500; // send binary data every .5 second
  - fromSampleRate: 44000 and you don't need to change it
  - you got binary data from `initWorker()` inside this function we call `socketSend(blob)` to send binary data to socket in dictate-service.js
  - we send 16000 binary data to engine through socket.
  
- `live-transcribe-vue/src/services/endpoint.js`
  - you can change socket and save endpoint through endpoint.js file via `socketBaseURL`and `modifying` properties.
