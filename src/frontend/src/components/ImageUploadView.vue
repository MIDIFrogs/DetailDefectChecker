<template>
  <div class="image-upload-view">
    <div class="drop-area" @dragover.prevent @drop.prevent="handleDrop" @click="openFileExplorer">
      <div class="upload-icon">
        <i class="fas fa-cloud-upload-alt"></i>
      </div>
      <p>Drop your images here or click to select</p>
      <input type="file" ref="fileInput" @change="handleFileSelect" multiple style="display: none;" />
    </div>
    <button @click="uploadImages">Upload</button>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { processImage } from '../api';

export default defineComponent({
  name: 'ImageUploadView',
  setup() {
    const files = ref<File[]>([]);
    const fileInput = ref<HTMLInputElement | null>(null);

    onMounted(() => {
      fileInput.value = document.querySelector('input[type="file"]') as HTMLInputElement;
    });

    const handleDrop = (event: DragEvent) => {
      files.value = Array.from(event.dataTransfer?.files || []);
    };

    const handleFileSelect = (event: Event) => {
      files.value = Array.from((event.target as HTMLInputElement).files || []);
    };

    const openFileExplorer = () => {
      fileInput.value?.click();
    };

    const uploadImages = async () => {
      for (const file of files.value) {
        try {
          await processImage(file);
          // Handle successful image processing
        } catch (error) {
          console.error('Error processing image:', error);
        }
      }
    };

    return {
      files,
      fileInput,
      handleDrop,
      handleFileSelect,
      openFileExplorer,
      uploadImages
    };
  }
});
</script>

<style scoped>
.image-upload-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.drop-area {
  border: 2px dashed #ccc;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  border-radius: 1rem;
}


.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}
</style>
