import cv2
import numpy as np

def calculate_noise_metrics(pil_data):
    # Load the image
    image = np.array(pil_data)[:, :, ::-1].copy()

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the grayscale image
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Calculate the noise by subtracting the blurred image from the original grayscale image
    noise = gray_image - blurred_image

    # Calculate the mean and standard deviation of the noise
    mean_noise = np.mean(noise)
    std_noise = np.std(noise)

    return mean_noise, std_noise

def is_noisy(image_path, mean_noise_threshold=128, std_noise_threshold=128):
    """
    Checks if an image is noisy based on the calculated noise metrics.
    
    Args:
        image_path (str): Path to the image file.
        mean_noise_threshold (float): Threshold for the mean noise value.
        std_noise_threshold (float): Threshold for the standard deviation of the noise.
        
    Returns:
        bool: True if the image is noisy, False otherwise.
    """
    mean_noise, std_noise = calculate_noise_metrics(image_path)
    print("Noise:", mean_noise, std_noise)
    if mean_noise > mean_noise_threshold or std_noise > std_noise_threshold:
        return True
    else:
        return False