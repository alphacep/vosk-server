module.exports = {
  publicPath:'/',
  transpileDependencies: [
    'vuetify'
  ],
  lintOnSave:false,
  
  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: false
    }
  }
}
