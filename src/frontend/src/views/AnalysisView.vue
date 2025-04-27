<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { processImage, downloadImage, type ProcessedImage } from '../api';

interface ImageFile {
  id?: string;
  name: string;
  size: number;
  url?: string;
  uploadProgress?: number;
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
            size: file.size,
            uploadProgress: 0
          };
          
          selectedImages.value.push(newImage);
          
          // Process image through backend
          const processedData = await processImage(file, (progress: number) => {
            newImage.uploadProgress = progress;
          });
          
          newImage.id = processedData.id;
          newImage.detections = processedData.detections;
          
          // Get the image URL
          newImage.url = await downloadImage(processedData.downloadId);
          
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
            <div v-else-if="isLoading" class="loading-preview light-text">
              Loading...
            </div>
            <div v-else class="no-preview light-text">
              No image selected
            </div>
          </div>
        </section>

        <!-- Image List -->
        <section class="image-list-section">
          <div class="image-list-header">
            <h2>Загруженные изображения</h2>
          </div>
          <div class="image-list">
            <div
              v-for="(image, index) in selectedImages"
              :key="index"
              class="image-item"
              :class="{ active: image === currentImage }"
              @click="selectImage(image)"
            >
              <img
                v-if="image.url"
                :src="image.url"
                alt="Preview"
                class="preview-image"
              />
              <div v-else class="loading-preview light-text">
                Loading...
              </div>
              <span class="image-name light-text">{{ image.name }}</span>
              <button
                @click.stop="removeImage(index)"
                class="remove-button"
                title="Remove image"
              >×</button>
            </div>

            <label class="image-item add-more-button" :class="{ disabled: isLoading }">
              <span>+</span>
              <div class="light-text">{{ isLoading ? 'Загрузка...' : 'Добавить' }}</div>
              <input
                type="file"
                accept="image/*"
                multiple
                @change="handleNewFiles"
                class="hidden-input"
                :disabled="isLoading"
              >
              <div v-if="isLoading" class="upload-progress">
                <div class="upload-progress-bar" :style="{ width: '50%' }"></div>
                <div class="upload-progress-label light-text">Uploading...</div>
              </div>
            </label>
          </div>
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
                <span class="defect-status light-text" :class="{ failed: !detection.passed }">
                  {{ detection.passed ? 'Passed' : 'Failed' }}
                </span>
              </div>
              <div class="defect-details light-text">
                <div>Defects count: {{ detection.defectsCount }}</div>
                <div>Size: {{ detection.calculatedSize.width.toFixed(2) }}x{{ detection.calculatedSize.height.toFixed(2) }}</div>
                <div>Size check: {{ detection.sizePassed ? 'Passed' : 'Failed' }}</div>
                <div>Surface: {{ detection.isRough ? 'Rough' : 'Smooth' }}</div>
              </div>
            </div>
            <div v-else class="no-defects light-text">
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
  width: 100%;
  background: #FDF4E3;
}

.header {
  padding: 1.5rem 2rem;
  background: rgba(253, 244, 227, 0.8);
  width: 100%;
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
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: 1fr auto;
  gap: 2rem;
  height: calc(100vh - 200px);
}

.preview-section {
  grid-column: 1;
  grid-row: 1 / -1;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  overflow: hidden;
}

.preview-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(253, 244, 227, 0.5);
  border-radius: 12px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-preview, .loading-preview {
  color: #262626;
  font-size: 1.2rem;
}

.loading-preview {
  color: #729BAD;
}

.image-list-section {
  grid-column: 2;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 1rem;
}

.image-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.image-list-header h2 {
  color: #262626;
  font-size: 1.2rem;
  margin: 0;
}

.image-list {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.image-list::-webkit-scrollbar {
  width: 8px;
}

.image-list::-webkit-scrollbar-track {
  background: rgba(253, 244, 227, 0.5);
  border-radius: 4px;
}

.image-list::-webkit-scrollbar-thumb {
  background: #729BAD;
  border-radius: 4px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.image-item.active {
  border-color: #729BAD;
}

.image-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: rgba(253, 244, 227, 0.9);
  font-size: 0.8rem;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-button {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background: rgba(253, 244, 227, 0.9);
  border: none;
  color: #729BAD;
  width: 24px;
  height: 24px;
  border-radius: 12px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-item:hover .remove-button {
  opacity: 1;
}

.add-more-button {
  aspect-ratio: 1;
  background: rgba(114, 155, 173, 0.1);
  border: 2px dashed #729BAD;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  transition: all 0.3s ease;
  color: #729BAD;
}

.add-more-button:hover:not(.disabled) {
  background: rgba(114, 155, 173, 0.2);
}

.add-more-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-more-button span {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.upload-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(114, 155, 173, 0.2);
}

.upload-progress-bar {
  height: 100%;
  background: #729BAD;
  transition: width 0.3s ease;
}

.upload-progress-label {
  position: absolute;
  bottom: 1.5rem;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 0.8rem;
  color: #729BAD;
}

.defects-section {
  grid-column: 2;
  grid-row: 2;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 1rem;
  overflow-y: auto;
}

.defects-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.defect-item {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #838385;
  border-radius: 8px;
  padding: 1rem;
  color: #262626;
}

.defect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.defect-name {
  font-weight: 600;
  color: #262626;
}

.defect-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: #729BAD;
  color: white;
  font-size: 0.9rem;
}

.defect-status.failed {
  background: #838385;
}

.defect-details {
  font-size: 0.9rem;
  color: #262626;
  display: grid;
  gap: 0.25rem;
}

.defect-item.defect-failed {
  border-color: #838385;
  background: rgba(131, 131, 133, 0.1);
}

.defect-item.defect-rough {
  border-color: #729BAD;
  background: rgba(114, 155, 173, 0.1);
}

.no-defects {
  color: #262626;
  font-style: italic;
  text-align: center;
  padding: 1rem;
}
</style> 