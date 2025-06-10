import math
import cairo
import colorsys
from dataclasses import dataclass
from colorspace import HCL

def parse_css_color(css_color):
    """Parse CSS color string (rgb() or hex) to (r, g, b) tuple with values 0-1"""
    if css_color.startswith('rgb('):
        # Remove 'rgb(' and ')' and split by commas
        rgb_str = css_color.replace('rgb(', '').replace(')', '')
        r, g, b = map(int, rgb_str.split(', '))
        return r/255.0, g/255.0, b/255.0
    elif css_color.startswith('#'):
        # Parse hex color
        hex_color = css_color[1:]  # Remove '#'
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return r/255.0, g/255.0, b/255.0
        elif len(hex_color) == 3:
            r = int(hex_color[0], 16) * 17  # Convert single digit to double
            g = int(hex_color[1], 16) * 17
            b = int(hex_color[2], 16) * 17
            return r/255.0, g/255.0, b/255.0

    # Fallback to gray if parsing fails
    return 0.5, 0.5, 0.5

@dataclass
class Cube:
    """Represents a cube with position and color"""
    x: float
    y: float
    z: float
    color: tuple[float, float, float]

    @property
    def position(self) -> tuple[float, float, float]:
        """Get the cube's position as a tuple"""
        return (self.x, self.y, self.z)

def project_orthographic(x, y, z, viewpoint, scale=1.0):
    """
    Project 3D point to 2D using orthographic projection from a viewpoint

    Args:
        x, y, z: 3D point coordinates
        viewpoint: (vx, vy, vz) - viewing direction (normalized)
        scale: scaling factor for the projection

    Returns:
        (px, py) - 2D projected coordinates
    """
    vx, vy, vz = viewpoint

    # Normalize viewing direction
    length = math.sqrt(vx*vx + vy*vy + vz*vz)
    if length > 0:
        vx, vy, vz = vx/length, vy/length, vz/length

    # Create two orthogonal vectors to the viewing direction
    # Choose an arbitrary vector not parallel to viewing direction
    if abs(vx) < 0.9:
        temp = (1, 0, 0)
    else:
        temp = (0, 1, 0)

    # Create first orthogonal vector (right)
    rx = temp[1]*vz - temp[2]*vy
    ry = temp[2]*vx - temp[0]*vz
    rz = temp[0]*vy - temp[1]*vx
    r_length = math.sqrt(rx*rx + ry*ry + rz*rz)
    if r_length > 0:
        rx, ry, rz = rx/r_length, ry/r_length, rz/r_length

    # Create second orthogonal vector (up)
    ux = ry*vz - rz*vy
    uy = rz*vx - rx*vz
    uz = rx*vy - ry*vx

    # Project point onto the two orthogonal vectors
    px = scale * (x*rx + y*ry + z*rz)
    py = scale * (x*ux + y*uy + z*uz)

    return px, py

def generate_hauy_octahedron_cubes(layers=3, color_scheme='depth'):
    """
    Generate cube objects for Haüy construction of octahedron

    Args:
        layers: number of layers in the octahedron (odd number recommended)
        color_scheme: 'depth', 'height', or 'uniform'

    Returns:
        list of Cube objects
    """
    cubes = []
    center = layers // 2

    for layer in range(layers):
        # Distance from center layer
        dist_from_center = abs(layer - center)
        # Size of square at this layer
        size = layers - dist_from_center

        # Generate square grid of cubes for this layer
        start = -size // 2
        end = size // 2

        for i in range(start, end + 1):
            for j in range(start, end + 1):
                # Only include cubes that are within the octahedral boundary
                if abs(i) + abs(j) + dist_from_center <= center:
                    x = i
                    y = layer - center  # Convert layer to y coordinate
                    z = j

                    # Calculate color based on scheme
                    color = _calculate_cube_color(x, y, z, color_scheme)
                    cubes.append(Cube(x, y, z, color))

    return cubes

def generate_hauy_octahedron_cubes_classic(n=2, color_scheme='depth'):
    """
    Generate classic Haüy octahedron with n layers on each side
    The octahedron has 2n+1 total layers
    """
    cubes = []

    # For each layer from bottom to top
    for y in range(-n, n + 1):
        # Maximum extent at this layer
        max_extent = n - abs(y)

        # Generate all cubes in this layer
        for x in range(-max_extent, max_extent + 1):
            for z in range(-max_extent, max_extent + 1):
                # Only include cubes within octahedral boundary
                if abs(x) + abs(z) <= max_extent:
                    # Calculate color based on scheme
                    color = _calculate_cube_color(x, y, z, color_scheme)
                    cubes.append(Cube(x, y, z, color))

    return cubes

def _calculate_cube_color(x, y, z, color_scheme):
    """Calculate color for a cube based on position and color scheme"""
    if color_scheme == 'depth':
        # Color by y-position (height), brighter at top, darker at bottom
        height_factor = (y + 3) / 6  # Normalize to 0-1, bottom=0, top=1
        # Use perceptual HCL color space with vibrant colors
        # Use blue hue (240°) with high chroma and varying luminance
        hue = 240
        chroma = 90  # Increased for more colorful appearance
        luminance = 25 + height_factor * 60  # 25-85 range, brighter at top (y=3), darker at bottom (y=-3)

        hcl_color = HCL([hue], [chroma], [luminance])
        css_color = hcl_color.colors()[0]
        return parse_css_color(css_color)
    elif color_scheme == 'height':
        # Color by y-position
        height_factor = (y + 3) / 6
        return (0.7 + 0.3 * height_factor, 0.3 + 0.4 * height_factor, 0.3 + 0.2 * height_factor)
    elif color_scheme == 'distance':
        # Color by Manhattan distance from center (onion layers)
        distance = abs(x) + abs(y) + abs(z)
        distance += .5
        hue = (distance / 5) * 360

        # Use HCL for perceptually uniform colors
        chroma = 95  # Increased for more vibrant colors
        height_factor = (x + 3) / 6     # ranges 0-1
        luminance = 55 + height_factor * 20  # Vary luminance with height

        hcl_color = HCL([hue], [chroma], [luminance])
        css_color = hcl_color.colors()[0]
        return parse_css_color(css_color)
    else:
        # Default blue
        return (0.6, 0.8, 1.0)

def draw_cube_at_position(ctx, cube, cube_size, gap, viewpoint, scale, stroke_width, offset_x, offset_y):
    """Draw a single cube using orthographic projection from viewpoint"""
    x_pos, y_pos, z_pos = cube.position

    # Define cube vertices relative to position
    half = cube_size / 2
    vertices = []
    for dx, dy, dz in [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                       (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]:
        x = x_pos * (cube_size + gap) + dx * half
        y = y_pos * (cube_size + gap) + dy * half
        z = z_pos * (cube_size + gap) + dz * half
        vertices.append((x, y, z))

    # Apply orthographic projection
    projected = []
    for x, y, z in vertices:
        px, py = project_orthographic(x, y, z, viewpoint, scale)
        projected.append((px + offset_x, py + offset_y))

    # Use the cube's stored color
    color = cube.color

    # Determine which faces are visible based on viewing direction
    vx, vy, vz = viewpoint
    # Normalize viewing direction
    length = math.sqrt(vx*vx + vy*vy + vz*vz)
    if length > 0:
        vx, vy, vz = vx/length, vy/length, vz/length

    faces = []
    # Face normals (pointing outward from cube)
    face_normals = [
        (0, 0, -1),  # back face (negative z)
        (1, 0, 0),   # right face (positive x)
        (0, 0, 1),   # front face (positive z)
        (-1, 0, 0),  # left face (negative x)
        (0, 1, 0),   # top face (positive y)
        (0, -1, 0)   # bottom face (negative y)
    ]

    face_vertices = [
        [0, 3, 2, 1],  # back face
        [1, 2, 6, 5],  # right face
        [4, 5, 6, 7],  # front face
        [0, 4, 7, 3],  # left face
        [3, 7, 6, 2],  # top face
        [0, 1, 5, 4]   # bottom face
    ]

    face_colors = [
        [c * 0.6 for c in color],  # back (darker)
        [c * 0.8 for c in color],  # right
        [c * 0.9 for c in color],  # front (brightest)
        [c * 0.7 for c in color],  # left
        [c * 1.0 for c in color],  # top (brightest)
        [c * 0.5 for c in color]   # bottom (darkest)
    ]

    # Only draw faces that are facing toward the viewer
    for i, (nx, ny, nz) in enumerate(face_normals):
        # Dot product of face normal with viewing direction
        # If positive, face is pointing toward viewer
        dot_product = nx * (-vx) + ny * (-vy) + nz * (-vz)
        if dot_product > 0:
            faces.append((face_vertices[i], face_colors[i]))

    # Draw filled faces
    for face_vertices, face_color in faces:
        ctx.set_source_rgb(*face_color)

        # Move to first vertex
        x, y = projected[face_vertices[0]]
        ctx.move_to(x, y)

        # Draw to other vertices
        for vertex_idx in face_vertices[1:]:
            x, y = projected[vertex_idx]
            ctx.line_to(x, y)

        ctx.close_path()
        ctx.fill_preserve()

        # Draw outline
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()

def create_hauy_octahedron_svg(filename, n=2, viewpoint=(1, 1, 1), scale=20, cube_size=20, gap=2, stroke_width=1, color_scheme='depth'):
    """
    Create SVG of Haüy octahedron construction using orthographic projection from viewpoint

    Args:
        filename: output SVG filename
        n: octahedron parameter (creates 2n+1 layers)
        viewpoint: (x, y, z) viewing direction (will be normalized)
        scale: scaling factor for the projection
        cube_size: size of individual cubes
        gap: space between cubes
        stroke_width: line thickness
        color_scheme: 'depth', 'height', or 'uniform'
    """

    # Generate cubes
    cubes = generate_hauy_octahedron_cubes_classic(n, color_scheme)

    # Calculate all projected positions to determine bounds
    all_projected = []
    for cube in cubes:
        x_pos, y_pos, z_pos = cube.position
        half = cube_size / 2

        # Check all 8 vertices of each cube
        for dx, dy, dz in [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                           (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]:
            x = x_pos * (cube_size + gap) + dx * half
            y = y_pos * (cube_size + gap) + dy * half
            z = z_pos * (cube_size + gap) + dz * half

            px, py = project_orthographic(x, y, z, viewpoint, scale)
            all_projected.append((px, py))

    # Calculate bounds
    min_x = min(p[0] for p in all_projected)
    max_x = max(p[0] for p in all_projected)
    min_y = min(p[1] for p in all_projected)
    max_y = max(p[1] for p in all_projected)

    width = max_x - min_x + 40
    height = max_y - min_y + 40
    offset_x = 20 - min_x
    offset_y = 20 - min_y

    # Create SVG surface and context
    surface = cairo.SVGSurface(filename, width, height)
    ctx = cairo.Context(surface)
    ctx.set_line_width(stroke_width * 0.5)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Sort cubes by depth along viewing direction for proper rendering (back to front)
    def cube_depth_along_view(cube):
        x, y, z = cube.position
        # Calculate center of cube
        x_center = x * (cube_size + gap)
        y_center = y * (cube_size + gap)
        z_center = z * (cube_size + gap)

        # Calculate depth along viewing direction
        vx, vy, vz = viewpoint
        # Normalize viewing direction
        length = math.sqrt(vx*vx + vy*vy + vz*vz)
        if length > 0:
            vx, vy, vz = vx/length, vy/length, vz/length

        # Dot product gives depth along viewing direction
        return x_center*vx + y_center*vy + z_center*vz

    sorted_cubes = sorted(cubes, key=cube_depth_along_view, reverse=True)

    # Draw all cubes
    for cube in sorted_cubes:
        draw_cube_at_position(ctx, cube, cube_size, gap, viewpoint, scale, stroke_width, offset_x, offset_y)

    surface.finish()

    return len(cubes)

# Example usage
if __name__ == "__main__":
    # Define viewpoint to show octahedron with brightest cube at very top
    viewpoint = (-0.5, -0.8, .5)  # Adjusted x component to rotate view so apex is at top

    # Generate different sizes of Haüy octahedra
    for n in [0, 1, 2, 3]:
        cube_count = create_hauy_octahedron_svg(
            f'{n}.svg',
            n=n,
            viewpoint=viewpoint,
            scale=5,
            cube_size=15,
            gap=3,
            color_scheme='distance'
        )
        print(f"Haüy octahedron (n={n}) with {cube_count} cubes saved as '{n}.svg'")

    # # Generate with different color schemes
    # create_hauy_octahedron_svg('hauy_octahedron_height.svg', n=3, viewpoint=viewpoint, scale=15, gap=3, color_scheme='height')
    # print("Height-colored octahedron saved as 'hauy_octahedron_height.svg'")
    #
    # # Generate with distance-based hue coloring
    # create_hauy_octahedron_svg('hauy_octahedron_distance.svg', n=3, viewpoint=viewpoint, scale=15, gap=3, color_scheme='distance')
    # print("Distance-colored octahedron saved as 'hauy_octahedron_distance.svg'")
    #
    # # Generate with no gap for comparison
    # create_hauy_octahedron_svg('hauy_octahedron_solid.svg', n=3, viewpoint=viewpoint, scale=15, gap=0, color_scheme='depth')
    # print("Solid octahedron (no gaps) saved as 'hauy_octahedron_solid.svg'")
    #
    # print("\nHaüy construction shows how an octahedron can be built from cubic units.")
    # print("Try different viewing directions like (1, 0, 1), (0, 1, 1), or (2, 1, 1) for different angles!")
    # print("Adjust scale parameter to make the drawing larger or smaller.")
