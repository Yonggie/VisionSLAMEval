# Usage examples:
# python vis.py cloud1.ply
# python vis.py cloud1.ply cloud2.ply cloud3.ply

# Note: Open3D colors must be in [0,1] range in float64
import open3d as o3d
import argparse
import os
import numpy as np


def load_ply_with_normalized_colors(ply_path):
    """Load a single PLY file and ensure its colors are in the [0,1] range."""
    pcd = o3d.io.read_point_cloud(ply_path)
    
    if pcd.is_empty():
        print(f"Warning: {ply_path} is empty or failed to load.")
        return None

    if pcd.has_colors():
        colors_np = np.asarray(pcd.colors)
        # Check if colors are in the 0-255 range and normalize them
        if colors_np.size > 0 and colors_np.max() > 1.0:
            print(f"Normalizing colors of {os.path.basename(ply_path)} to [0, 1].")
            colors_np = colors_np / 255.0
            # Ensure values do not exceed [0,1]
            colors_np = np.clip(colors_np, 0.0, 1.0)
            pcd.colors = o3d.utility.Vector3dVector(colors_np)
    else:
        print(f"{os.path.basename(ply_path)} has no colors. Using default gray.")
        # Assign a default gray color if no colors are present
        pcd.paint_uniform_color([0.5, 0.5, 0.5])

    return pcd


def main():
    parser = argparse.ArgumentParser(description="Visualize one or more .ply point cloud files")
    parser.add_argument("paths", nargs='+', type=str,
                        help="Paths to one or multiple .ply files")
    parser.add_argument("--point_size", type=int, default=2,
                        help="Point size (default: 2)")
    args = parser.parse_args()

    all_pcds = []

    # Iterate through all provided file paths
    for path in args.paths:
        if not os.path.exists(path):
            print(f"Error: Path {path} does not exist. Skipping.")
            continue

        # Only process .ply files
        if path.lower().endswith('.ply'):
            pcd = load_ply_with_normalized_colors(path)
            if pcd is not None:
                all_pcds.append(pcd)
        else:
            print(f"Warning: {path} is not a .ply file. Skipping.")

    if not all_pcds:
        print("Error: No valid point clouds loaded!")
        return

    print(f"Total loaded point clouds: {len(all_pcds)}")

    # Create Open3D visualizer
    vis = o3d.visualization.Visualizer()
    window_title = ", ".join(os.path.basename(p) for p in args.paths)
    vis.create_window(window_title, width=1280, height=720)
    
    # Add all loaded geometries to the visualizer
    for pcd in all_pcds:
        vis.add_geometry(pcd)
        
    # Set rendering options
    vis.get_render_option().point_size = args.point_size
    vis.get_render_option().background_color = [1.0, 1.0, 1.0]  # White background

    # Run the visualization loop
    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    main()