import axios, { type AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Accept': 'application/json',
    'Access-Control-Allow-Origin': '*'
  }
});

export interface ProcessedImage {
  id: string;
  detections: Array<{
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
  detectionsCount: number;
  passedCount: number;
  downloadId: string;
}

export const processImage = async (image: File): Promise<ProcessedImage> => {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('scale_x', '0.01');
  formData.append('scale_y', '0.01');

  const response = await api.post('/process', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};

export const downloadImage = async (imageId: string): Promise<string> => {
  const response = await api.get(`/download/${imageId}`, {
    responseType: 'blob'
  });
  return URL.createObjectURL(response.data);
};
