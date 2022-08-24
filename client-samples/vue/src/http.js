import Vue from "vue";
import axios from "axios";

const $domain_api = "http://localhost:8080";

const base = axios.create({
    baseURL: $domain_api,
    headers: {
        'lang': 'ar'
    }
});

base.interceptors.request.use((config) => {

    return config;
});
base.interceptors.response.use(
    function(response) {
        // Any status code that lie within the range of 2xx cause this function to trigger
        // Do something with response data
        //    store.dispatch('toggleHide');

        return response.data;
    },
    function(error) {

        //   //console.log(error.response);
        return Promise.reject(error);
    }
);


Vue.prototype.$http = base;
export default base;