import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router';
import ImageUploadView from './components/ImageUploadView.vue';
// import UploadAndProcessingProgressView from './components/UploadAndProcessingProgressView.vue';
// import ResultsView from './components/ResultsView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'ImageUpload',
    component: ImageUploadView
  },
  // {
  //   path: '/progress',
  //   name: 'UploadAndProcessingProgress',
  //   component: UploadAndProcessingProgressView
  // },
  // {
  //   path: '/results',
  //   name: 'Results',
  //   component: ResultsView
  // }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
