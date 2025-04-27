<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { processImage } from '../api';

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
      <h1>Image Analyzer</h1>
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
          <i class="upload-icon">📁</i>
          <p>Перетащите изображения сюда или</p>
          <label class="upload-button">
            Выбрать файл
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
.upload-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1.5rem 2rem;
  background: white;
}

.header h1 {
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
  max-width: 1920px;
  margin: 0;
  width: 100%;
  text-align: left;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 80px);
}

.drop-zone {
  width: 80%;
  height: 70vh;
  border: 2px dashed #ccc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
}

.drop-zone.is-dragging {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.drop-zone-content {
  text-align: center;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  display: block;
}

.upload-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1.5rem;
  transition: background-color 0.3s ease;
  font-size: 1.1rem;
}

.upload-button:hover {
  background: #45a049;
}

.hidden-input {
  display: none;
}
</style> 