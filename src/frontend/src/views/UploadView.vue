<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { processImage } from '../api';
import UploadIcon from '../assets/UploadIcon.svg';

const router = useRouter();
const isDragging = ref(false);

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
};

const handleDrop = async (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files?.length) {
    await handleFiles(Array.from(files));
  }
};

const handleFileSelect = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    await handleFiles(Array.from(input.files));
  }
};

const handleFiles = async (files: File[]) => {
  try {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    if (imageFiles.length === 0) {
      alert('Please select image files only');
      return;
    }

    // Store files in state management (we'll implement this later)
    localStorage.setItem('uploadedImages', JSON.stringify(
      imageFiles.map(file => ({ name: file.name, size: file.size }))
    ));

    // Process first image
    await processImage(imageFiles[0]);
    
    // Navigate to analysis page
    router.push('/analysis');
  } catch (error) {
    console.error('Error processing images:', error);
    alert('Error processing images. Please try again.');
  }
};
</script>

<template>
  <div class="upload-view">
    <header class="header">
      <div class="header-content">
        <h1>Image Analyzer</h1>
      </div>
    </header>

    <main class="main-content">
      <div
        class="drop-zone"
        :class="{ 'is-dragging': isDragging }"
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
        @dragover.prevent
        @drop="handleDrop"
      >
        <div class="drop-zone-content">
          <img :src="UploadIcon" alt="Upload" class="upload-icon" />
          <p class="medium-text">Перетащите изображение</p>
          <p class="light-text">или нажмите сюда</p>
          <label class="upload-button">
            <span class="regular-text">Выбрать файл</span>
            <input
              type="file"
              accept="image/*"
              multiple
              @change="handleFileSelect"
              class="hidden-input"
            >
          </label>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.medium-text {
  font-weight: 500;
}

.light-text {
  font-weight: 300;
}

.regular-text {
  font-weight: 400;
}

.upload-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  background: #FDF4E3;
}

.header {
  padding: 1.5rem 2rem;
  background: rgba(253, 244, 227, 0.8);
  width: 100%;
}

.header-content {
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
}

.header h1 {
  color: #262626;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: left;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 80px);
  width: 100%;
  padding: 2rem;
  box-sizing: border-box;
}

.drop-zone {
  width: 80%;
  max-width: 1920px;
  height: 70vh;
  border: 4px dashed #838385;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: rgba(253, 244, 227, 0.5);
}

.drop-zone.is-dragging {
  border-color: #729BAD;
  background: rgba(253, 244, 227, 0.7);
}

.drop-zone-content {
  text-align: center;
  width: 100%;
  padding: 2rem;
  color: #262626;
}

.drop-zone-content p {
  margin: 0.5rem 0;
}

.upload-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  color: #729BAD;
}

.upload-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #729BAD;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1.5rem;
  transition: background-color 0.3s ease;
  font-size: 1.1rem;
}

.upload-button:hover {
  background: #60859e;
}

.hidden-input {
  display: none;
}
</style> 