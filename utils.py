import cv2
import os

def get_list_of_presentation_images(folder_path):
    try:
        path_images = sorted(os.listdir(folder_path), key=len)
    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found. Please check the path.")
        exit()
    return path_images

def draw_circle(image, center, radius, color, thickness=-1):
    cv2.circle(image, center, radius, color, thickness)

def draw_line(image, start_point, end_point, color, thickness=2):
    cv2.line(image, start_point, end_point, color, thickness)