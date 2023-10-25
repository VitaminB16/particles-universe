from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx


def mp4_to_gif(input_file, output_file, skip_frames=1, resize=1):
    """
    Convert MP4 video to GIF.

    Parameters:
    - input_file: str: path to the input .mp4 file
    - output_file: str: path to the output .gif file
    - skip_frames: int: keep every Nth frame (e.g., 2 will keep every second frame)
    - resize: int: downscaling factor (e.g., 2 will reduce both width and height by half)
    """
    with VideoFileClip(input_file) as clip:
        # Only keep every Nth frame
        # duration = clip.duration
        if skip_frames > 1:
            clip = clip.fx(vfx.speedx, skip_frames)

        # clip.duration = duration // skip_frames
        # Resize the clip based on the downscaling factor
        if resize != 1:
            clip = clip.resize(1 / resize)

        clip.write_gif(output_file, fps=60 // skip_frames)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:][0]
    mp4_to_gif(args, args.replace(".mp4", ".gif"), skip_frames=3, resize=2)
