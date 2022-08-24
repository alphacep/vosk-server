import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";

/*
*No stacktrace on NavigationDuplicated error uncaught in promise

*If you want to handle this globally, you can replace Router's 
push/replace functions to silence the rejection and make the 
promise resolve with the error instead:
*/
const originalPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
};


Vue.use(VueRouter);

const routes = [
  // =============================================================================
  // MAIN LAYOUT ROUTES
  // =============================================================================
  { path: '/', component: Home, redirect: '/home' },

      {
        path: "/home",
        name: "Home",
        component: Home,
      },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,

  scrollBehavior() {
    return { x: 0, y: 0 };
  },
  routes,
});
router.afterEach((to, from, next) => {
  setTimeout(() => {
    const nearestWithTitle = to.matched
      .slice()
      .reverse()
      .find((r) => r.meta && r.meta.title);
    if (nearestWithTitle) document.title = i18n.t(nearestWithTitle.meta.title);
  });
});



export default router;
