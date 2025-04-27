import axios, { type AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: 'https://localhost:/api'
});

export const processImage = (image: File): Promise<any> => {
  const formData = new FormData();
  formData.append('image', image);

  return api.post('/process', formData);
};

export const downloadImage = (imageId: string): Promise<any> => {
  return api.get(`/download-image/${imageId}`);
};
