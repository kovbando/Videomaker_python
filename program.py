import os
import subprocess
from collections import defaultdict
import time
from concurrent.futures import ThreadPoolExecutor

def get_current_directory():
    """Returns the current directory of the script."""
    return os.path.dirname(os.path.abspath(__file__))

def get_images_from_folder(folder_path):
    """Fetches image files from the given folder."""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(valid_extensions)]

def group_images_by_developer(images, limit=10000000):
    """Groups images by developer based on the filename, limiting the number of images per developer."""
    grouped_images = defaultdict(list)
    for img_path in images:
        filename = os.path.basename(img_path)
        parts = filename.split('_')
        if parts[0].startswith('Dev'):
            dev_indicator = parts[0]
            grouped_images[dev_indicator].append(img_path)
        else:
            print(f"Skipping invalid file: {filename}")
    
    # Limit the number of images per developer
    for dev in grouped_images:
        grouped_images[dev] = grouped_images[dev][:limit]
    
    return grouped_images

def create_ffmpeg_input_file(group, group_index, temp_dir):
    """Creates a temporary input file for FFmpeg based on the image group."""
    input_file_path = os.path.join(temp_dir, f"group_{group_index}.txt")
    with open(input_file_path, "w") as f:
        for img_path in group:
            f.write(f"file '{img_path}'\n")
    return input_file_path

def create_video_from_group(group, group_index, frame_rate, temp_dir, ffmpeg_path):
    """Creates an individual video from the image group using FFmpeg."""
    input_file = create_ffmpeg_input_file(group, group_index, temp_dir)
    intermediate_video = os.path.join(temp_dir, f"group_{group_index}.mp4")

    cmd = [
        ffmpeg_path, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", input_file,
        "-vf", "scale=960:-1",
        "-r", str(frame_rate),
        intermediate_video
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        print(f"[{time.strftime('%H:%M:%S')}] Created video for group {group_index + 1}")
    except subprocess.CalledProcessError as e:
        print(f"Error while creating video for group {group_index + 1}: {e}")
        print(f"FFmpeg stderr: {e.stderr.decode()}")

    return intermediate_video

def create_video_from_grouped_images(groups, output_path, frame_rate, temp_dir, ffmpeg_path):
    """Creates a video from image groups and combines them into a 2x2 grid."""
    os.makedirs(temp_dir, exist_ok=True)
    intermediate_videos = []

    # Step 1: Create individual videos for each group in parallel
    print(f"[{time.strftime('%H:%M:%S')}] Starting to create individual videos...")
    start_time = time.time()

    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor() as executor:
        intermediate_videos = list(executor.map(
            lambda idx_group: create_video_from_group(idx_group[1], idx_group[0], frame_rate, temp_dir, ffmpeg_path),
            enumerate(groups)
        ))

    print(f"Time taken to create individual videos: {time.time() - start_time:.2f} seconds")

    # Step 2: Combine videos into a 2x2 grid
    print(f"[{time.strftime('%H:%M:%S')}] Combining videos into a 2x2 grid...")
    start_time = time.time()

    input_cmds = sum([["-i", video] for video in intermediate_videos], [])
    grid_cmd = [
        ffmpeg_path, "-y", *input_cmds,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-filter_complex", (
            "nullsrc=size=1920x1080 [base];"
            "[3:v] setpts=PTS-STARTPTS, scale=960x540 [upperleft];"
            "[0:v] setpts=PTS-STARTPTS, scale=960x540 [upperright];"
            "[1:v] setpts=PTS-STARTPTS, scale=960x540 [lowerleft];"
            "[2:v] setpts=PTS-STARTPTS, scale=960x540 [lowerright];"
            "[base][upperleft] overlay=shortest=1 [tmp1];"
            "[tmp1][upperright] overlay=W/2:0 [tmp2];"
            "[tmp2][lowerleft] overlay=0:H/2 [tmp3];"
            "[tmp3][lowerright] overlay=W/2:H/2"
        ),
        output_path
    ]
    
    try:
        result = subprocess.run(grid_cmd, check=True, capture_output=True)
        print(result.stderr.decode())  # Output FFmpeg errors, if any
    except subprocess.CalledProcessError as e:
        print(f"Error while combining videos: {e}")
        print(f"FFmpeg stderr: {e.stderr.decode()}")
        return

    print(f"Time taken to combine videos into a 2x2 grid: {time.time() - start_time:.2f} seconds")

def main():
    """Main function to execute the video creation process."""
    current_dir = get_current_directory()
    img_folder = os.path.join(current_dir, "pictures")
    output_video = os.path.join(current_dir, "dev_grouped_video.mp4")
    temp_dir = os.path.join(current_dir, "temp")
    frame_rate = 30

    # Path to the local FFmpeg binary
    ffmpeg_path = os.path.join(current_dir, "ffmpeg", "bin", "ffmpeg")  # Modify based on actual location of ffmpeg binary

    print(f"[{time.strftime('%H:%M:%S')}] Starting process...")
    start_time = time.time()

    # Fetch and group images
    images = get_images_from_folder(img_folder)
    
    grouped_images = group_images_by_developer(images, limit=20000000)
    groups = list(grouped_images.values())[:4]  # Use the first 4 groups for the grid

    # Create the final video
    create_video_from_grouped_images(groups, output_video, frame_rate, temp_dir, ffmpeg_path)

    print(f"[{time.strftime('%H:%M:%S')}] Process completed in {time.time() - start_time:.2f} seconds.")
    print(f"Video saved to: {output_video}")

if __name__ == "__main__":
    main()
