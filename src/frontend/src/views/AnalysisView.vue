<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { processImage, downloadImage, type ProcessedImage } from '../api';

interface ImageFile {
  id?: string;
  name: string;
  size: number;
  url?: string;
  detections?: Array<{
    bbox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    calculatedSize: {
      width: number;
      height: number;
    };
    className: string;
    defectsCount: number;
    isRough: boolean;
    passed: boolean;
    sizePassed: boolean;
  }>;
}

const router = useRouter();
const selectedImages = ref<ImageFile[]>([]);
const currentImage = ref<ImageFile | null>(null);
const isLoading = ref(false);

onMounted(async () => {
  const storedImages = localStorage.getItem('uploadedImages');
  if (storedImages) {
    selectedImages.value = JSON.parse(storedImages);
    if (selectedImages.value.length > 0) {
      await selectImage(selectedImages.value[0]);
    }
  } else {
    router.push('/');
  }
});

const selectImage = async (image: ImageFile) => {
  if (!image.url && image.id) {
    try {
      image.url = await downloadImage(image.id);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  }
  currentImage.value = image;
};

const handleNewFiles = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    isLoading.value = true;
    try {
      for (const file of Array.from(input.files)) {
        if (file.type.startsWith('image/')) {
          const newImage: ImageFile = {
            name: file.name,
            size: file.size
          };
          
          // Process image through backend
          const processedData = await processImage(file);
          newImage.id = processedData.downloadId;
          newImage.detections = processedData.detections;
          
          // Get the image URL
          newImage.url = await downloadImage(processedData.downloadId);
          
          selectedImages.value.push(newImage);
          if (!currentImage.value) {
            currentImage.value = newImage;
          }
        }
      }
      localStorage.setItem('uploadedImages', JSON.stringify(selectedImages.value));
    } catch (error) {
      console.error('Error processing images:', error);
      alert('Error processing images. Please try again.');
    } finally {
      isLoading.value = false;
    }
  }
};

const removeImage = (index: number) => {
  const removedImage = selectedImages.value[index];
  selectedImages.value.splice(index, 1);
  localStorage.setItem('uploadedImages', JSON.stringify(selectedImages.value));
  
  if (currentImage.value === removedImage) {
    currentImage.value = selectedImages.value[0] || null;
  }
  
  if (selectedImages.value.length === 0) {
    router.push('/');
  }
};
</script>

<template>
  <div class="analysis-view">
    <header class="header">
      <h1>Image Analyzer</h1>
    </header>

    <main class="main-content">
      <div class="content-grid">
        <!-- Image Preview -->
        <section class="preview-section">
          <div class="preview-container">
            <img
              v-if="currentImage?.url"
              :src="currentImage.url"
              alt="Preview"
              class="preview-image"
            />
            <div v-else-if="isLoading" class="loading-preview">
              Loading...
            </div>
            <div v-else class="no-preview">
              No image selected
            </div>
          </div>
        </section>

        <!-- Image List -->
        <section class="image-list-section">
          <h2>Загруженные изображения</h2>
          <div class="image-list">
            <div
              v-for="(image, index) in selectedImages"
              :key="index"
              class="image-item"
              :class="{ active: image === currentImage }"
              @click="selectImage(image)"
            >
              <span class="image-name">{{ image.name }}</span>
              <button
                @click.stop="removeImage(index)"
                class="remove-button"
                title="Remove image"
              >×</button>
            </div>
          </div>
          <label class="add-more-button" :class="{ disabled: isLoading }">
            {{ isLoading ? 'Загрузка...' : '+ Добавить еще' }}
            <input
              type="file"
              accept="image/*"
              multiple
              @change="handleNewFiles"
              class="hidden-input"
              :disabled="isLoading"
            >
          </label>
        </section>

        <!-- Defects List -->
        <section class="defects-section">
          <h2>Defects</h2>
          <div class="defects-list">
            <div
              v-if="currentImage?.detections?.length"
              v-for="(detection, index) in currentImage.detections"
              :key="index"
              class="defect-item"
              :class="{
                'defect-failed': !detection.passed,
                'defect-rough': detection.isRough
              }"
            >
              <div class="defect-header">
                <span class="defect-name">{{ detection.className }}</span>
                <span class="defect-status" :class="{ failed: !detection.passed }">
                  {{ detection.passed ? 'Passed' : 'Failed' }}
                </span>
              </div>
              <div class="defect-details">
                <div>Defects count: {{ detection.defectsCount }}</div>
                <div>Size: {{ detection.calculatedSize.width.toFixed(2) }}x{{ detection.calculatedSize.height.toFixed(2) }}</div>
                <div>Size check: {{ detection.sizePassed ? 'Passed' : 'Failed' }}</div>
                <div>Surface: {{ detection.isRough ? 'Rough' : 'Smooth' }}</div>
              </div>
            </div>
            <div v-else class="no-defects">
              {{ isLoading ? 'Analyzing defects...' : 'No defects detected' }}
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.analysis-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1.5rem 2rem;
  background: white;
}

.header h1 {
  color: #262626;
  font-size: 1.5rem;
  font-weight: 600;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  text-align: left;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr auto;
  gap: 2rem;
  height: calc(100vh - 200px);
}

.preview-section {
  grid-column: 1;
  grid-row: 1;
}

.preview-container {
  width: 100%;
  height: 100%;
  /*border: 1px solid #eee;*/
  /*border-radius: 8px;*/
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0);
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-preview, .loading-preview {
  color: #666;
  font-size: 1.2rem;
}

.loading-preview {
  color: #4CAF50;
}

.image-list-section {
  grid-column: 2;
  grid-row: 1;
}

.image-list {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: calc(100% - 100px);
  overflow-y: auto;
}

.image-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border: 1px solid #eee;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-item:hover {
  background: #f5f5f5;
}

.image-item.active {
  border-color: #4CAF50;
  background: #f0f7f0;
}

.image-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-button {
  background: none;
  border: none;
  color: #ff4444;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.5rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.remove-button:hover {
  opacity: 1;
}

.add-more-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-more-button:hover:not(.disabled) {
  background: #45a049;
}

.add-more-button.disabled {
  background: #ccc;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}

.defects-section {
  grid-column: 1 / -1;
  grid-row: 2;
}

.defects-list {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.defect-item {
  padding: 1rem;
  background: white;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 300px;
}

.defect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.defect-name {
  font-weight: 600;
}

.defect-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: #4CAF50;
  color: white;
  font-size: 0.9rem;
}

.defect-status.failed {
  background: #f44336;
}

.defect-details {
  font-size: 0.9rem;
  color: #666;
  display: grid;
  gap: 0.25rem;
}

.defect-item.defect-failed {
  border-color: #ffebee;
  background: #fff5f5;
}

.defect-item.defect-rough {
  border-color: #fff3e0;
  background: #fffaf3;
}

.no-defects {
  color: #666;
  font-style: italic;
}
</style> 