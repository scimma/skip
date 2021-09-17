// import axios from 'axios';
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css'  // This line and the following is necessary to get bootstrap working
import 'bootstrap-vue/dist/bootstrap-vue.css'
import AlertForm from './AlertForm.vue';

Vue.use(BootstrapVue);

Vue.config.productionTip = false


new Vue({
  render: h => h(AlertForm),
}).$mount('#alert-form')