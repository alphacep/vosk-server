import Vue from 'vue';

import Vuetify from 'vuetify/lib/framework';


Vue.use(Vuetify)

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#3082b1',
        dark_primary:'#1a4d6b',
        light_gray:'#ebeef4',
        evergreen:"#051925",
        warm_gray:'#969696',
        secondary: '#424242',
        accent: '#82B1FF',
        error: '#FF5252',
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#FB8C00',
        greyish_brown:"#4f4f4f"
      },
    },
  },
})