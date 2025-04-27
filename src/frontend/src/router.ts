import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router';
import UploadView from './views/UploadView.vue';
import AnalysisView from './views/AnalysisView.vue';
// import ImageUploadView from './components/ImageUploadView.vue';
// import UploadAndProcessingProgressView from './components/UploadAndProcessingProgressView.vue';
// import ResultsView from './components/ResultsView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Upload',
    component: UploadView
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: AnalysisView
  },

];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
