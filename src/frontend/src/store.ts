import { defineStore } from 'pinia';

export const useStore = defineStore('main', {
  state: () => ({
    uploadedImages: [] as File[],
    processingProgress: 0,
    processedImages: [] as any[]
  }),
  actions: {
    addUploadedImage(image: File) {
      this.uploadedImages.push(image);
    },
    setProcessingProgress(progress: number) {
      this.processingProgress = progress;
    },
    addProcessedImage(image: any) {
      this.processedImages.push(image);
    }
  }
});
