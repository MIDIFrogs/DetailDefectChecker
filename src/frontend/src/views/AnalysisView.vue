<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { processImage, downloadImage } from '../api';

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
  loadError?: boolean;
}

const router = useRouter();
const selectedImages = ref<ImageFile[]>([]);
const currentImageIndex = ref(0);
const isLoading = ref(false);

const currentImage = computed(() => {
  return selectedImages.value[currentImageIndex.value] || null;
});

onMounted(async () => {
  const storedImages = localStorage.getItem('uploadedImages');
  if (storedImages) {
    const parsedImages = JSON.parse(storedImages);
    if (parsedImages.length > 0) {
      // First set the images without URLs to show loading state
      selectedImages.value = parsedImages;
      
      // Then load all images in parallel
      await Promise.all(
        parsedImages.map(async (image: ImageFile, index: number) => {
          if (image.id) {
            try {
              const url = await downloadImage(image.id);
              // Update each image individually to maintain reactivity
              selectedImages.value[index] = {
                ...selectedImages.value[index],
                url
              };
            } catch (error) {
              console.error(`Error downloading image ${image.id}:`, error);
              // Keep the image in the list but mark it as failed
              selectedImages.value[index] = {
                ...selectedImages.value[index],
                loadError: true
              };
            }
          }
        })
      );
      currentImageIndex.value = 0;
    }
  } else {
    router.push('/');
  }
});

const selectImage = async (image: ImageFile, index: number) => {
  currentImageIndex.value = index;
  if (!image.url && image.id && !image.loadError) {
    try {
      const url = await downloadImage(image.id);
      // Update the image URL in the array to maintain reactivity
      selectedImages.value[index] = {
        ...selectedImages.value[index],
        url
      };
    } catch (error) {
      console.error(`Error downloading image ${image.id}:`, error);
      selectedImages.value[index] = {
        ...selectedImages.value[index],
        loadError: true
      };
    }
  }
};

const nextImage = () => {
  if (currentImageIndex.value < selectedImages.value.length - 1) {
    selectImage(selectedImages.value[currentImageIndex.value + 1], currentImageIndex.value + 1);
  }
};

const previousImage = () => {
  if (currentImageIndex.value > 0) {
    selectImage(selectedImages.value[currentImageIndex.value - 1], currentImageIndex.value - 1);
  }
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
            currentImageIndex.value = selectedImages.value.length - 1;
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
  selectedImages.value.splice(index, 1);
  localStorage.setItem('uploadedImages', JSON.stringify(selectedImages.value));
  
  if (currentImageIndex.value >= selectedImages.value.length) {
    currentImageIndex.value = Math.max(0, selectedImages.value.length - 1);
  }
  
  if (selectedImages.value.length === 0) {
    router.push('/');
  }
};
</script>

<template>
  <div class="analysis-view">
    <header class="header">
      <h1 class="medium-text">Image Analyzer</h1>
    </header>

    <main class="main-content">
      <div class="top-section">
        <!-- Main Image Preview -->
        <div class="preview-section">
          <div class="preview-container">
            <button 
              class="nav-button prev"
              :disabled="currentImageIndex === 0"
              @click="previousImage"
            >
              ←
            </button>
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
            <button 
              class="nav-button next"
              :disabled="currentImageIndex >= selectedImages.length - 1"
              @click="nextImage"
            >
              →
            </button>
          </div>
        </div>

        <!-- Image List Section -->
        <div class="image-list-section">
          <div class="image-list">
            <div
              v-for="(image, index) in selectedImages"
              :key="index"
              class="thumbnail-item"
              :class="{ active: index === currentImageIndex }"
              @click="selectImage(image, index)"
            >
              <img
                v-if="image.url"
                :src="image.url"
                :alt="image.name"
                class="thumbnail-image"
              />
              <div v-else-if="image.loadError" class="thumbnail-loading light-text error">
                Failed to load
              </div>
              <div v-else class="thumbnail-loading light-text">
                Loading...
              </div>
              <button
                @click.stop="removeImage(index)"
                class="remove-button"
                title="Remove image"
              >×</button>
            </div>

            <!-- Upload Button -->
            <label class="thumbnail-item upload-button" :class="{ disabled: isLoading }">
              <span class="plus-icon">+</span>
              <input
                type="file"
                accept="image/*"
                multiple
                @change="handleNewFiles"
                class="hidden-input"
                :disabled="isLoading"
              >
            </label>
          </div>

          <!-- Upload Progress -->
          <div v-if="isLoading" class="upload-progress-container">
            <div class="upload-progress">
              <div 
                class="upload-progress-bar" 
                :style="{ 
                  width: `${selectedImages[selectedImages.length - 1]?.uploadProgress || 0}%` 
                }"
              ></div>
            </div>
            <span class="upload-progress-text light-text">
              Uploading: {{ Math.round(selectedImages[selectedImages.length - 1]?.uploadProgress || 0) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Defects Section -->
      <section class="defects-section">
        <div class="defects-grid">
          <div
            v-if="currentImage?.detections?.length"
            v-for="(detection, index) in currentImage.detections"
            :key="index"
            class="defect-card"
            :class="{
              'defect-failed': !detection.passed,
              'defect-rough': detection.isRough
            }"
          >
            <div class="defect-header">
              <div class="defect-title">
                <h3 class="defect-name medium-text">{{ detection.className }}</h3>
                <div 
                  class="status-badge"
                  :class="{ 'status-passed': detection.passed, 'status-failed': !detection.passed }"
                >
                  {{ detection.passed ? 'ПРОЙДЕНО' : 'НЕ ПРОЙДЕНО' }}
                </div>
              </div>
            </div>
            <div class="defect-details light-text">
              <div class="detail-row">
                <span class="detail-label">Дефектов:</span>
                <span>{{ detection.defectsCount }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Размер:</span>
                <span>{{ detection.calculatedSize.width.toFixed(2) }}x{{ detection.calculatedSize.height.toFixed(2) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Проверка размера:</span>
                <span :class="detection.sizePassed ? 'passed' : 'failed'">
                  {{ detection.sizePassed ? 'Пройдена' : 'Не пройдена' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Поверхность:</span>
                <span>{{ detection.isRough ? 'Шероховатая' : 'Гладкая' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-defects light-text">
            {{ isLoading ? 'Анализ дефектов...' : 'Дефектов не обнаружено' }}
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.analysis-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #FDF4E3;
}

.header {
  padding: 1.5rem 2rem;
  background: rgba(253, 244, 227, 0.8);
  border-bottom: 1px solid rgba(131, 131, 133, 0.2);
}

.header h1 {
  max-width: 1920px;
  margin: 0 auto;
  color: #262626;
  font-size: 1.8rem;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.top-section {
  display: grid;
  grid-template-columns: 500px minmax(auto, 50vw);
  gap: 2rem;
  height: 500px;
  margin-bottom: 2rem;
}

/* Preview Section */
.preview-section {
  position: relative;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  overflow: hidden;
  height: 100%;
}

.preview-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(114, 155, 173, 0.9);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 20px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  z-index: 10;
}

.nav-button:hover {
  opacity: 1;
  background: #729BAD;
}

.nav-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-button.prev {
  left: 1rem;
}

.nav-button.next {
  right: 1rem;
}

/* Image List Section */
.image-list-section {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  overflow: hidden;
  height: 100%;
  max-width: 50vw;
  margin-left: auto;
}

.image-list {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(100% / 8), 1fr));
  gap: 0.75rem;
  padding: 1rem;
  overflow-y: auto;
  align-items: start;
  max-width: 50vw;
}

@media (max-width: 1600px) {
  .image-list {
    grid-template-columns: repeat(auto-fit, minmax(calc(100% / 6), 1fr));
  }
}

@media (max-width: 1200px) {
  .image-list {
    grid-template-columns: repeat(auto-fit, minmax(calc(100% / 4), 1fr));
  }
}

.thumbnail-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  min-height: 80px;
  max-height: 120px;
}

.thumbnail-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.thumbnail-item.active {
  border: 2px solid #729BAD;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-loading {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #729BAD;
  font-size: 0.8rem;
}

.remove-button {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background: rgba(253, 244, 227, 0.9);
  border: none;
  color: #729BAD;
  width: 20px;
  height: 20px;
  border-radius: 10px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.thumbnail-item:hover .remove-button {
  opacity: 1;
}

/* Upload Button */
.upload-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(114, 155, 173, 0.1);
  border: 2px dashed #729BAD;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-button:hover {
  background: rgba(114, 155, 173, 0.2);
}

.upload-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.plus-icon {
  font-size: 2rem;
  color: #729BAD;
}

/* Upload Progress */
.upload-progress-container {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-top: 1px solid rgba(131, 131, 133, 0.2);
}

.upload-progress {
  height: 4px;
  background: rgba(114, 155, 173, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.upload-progress-bar {
  height: 100%;
  background: #729BAD;
  transition: width 0.3s ease;
}

.upload-progress-text {
  display: block;
  text-align: center;
  font-size: 0.8rem;
  color: #729BAD;
}

/* Defects Section */
.defects-section {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  margin-left: 0;
  width: fit-content;
}

.defects-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: flex-start;
  max-width: 100%;
}

.defect-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  width: 300px;
  flex-shrink: 0;
}

.defect-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.defect-header {
  margin-bottom: 1rem;
}

.defect-title {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.defect-name {
  margin: 0;
  color: #262626;
  font-size: 1.2rem;
  flex-grow: 1;
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  font-weight: 500;
  white-space: nowrap;
}

.status-passed {
  background: rgba(75, 181, 67, 0.1);
  color: #4BB543;
}

.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.defect-details {
  display: grid;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.detail-label {
  color: rgba(38, 38, 38, 0.7);
}

.passed {
  color: #4BB543;
}

.failed {
  color: #EF4444;
}

.no-defects {
  width: 100%;
  text-align: left;
  padding: 1rem;
  color: #262626;
  font-style: italic;
}

.hidden-input {
  display: none;
}

.thumbnail-loading.error {
  color: #838385;
  font-size: 0.7rem;
  text-align: center;
  padding: 0.5rem;
}
</style> 