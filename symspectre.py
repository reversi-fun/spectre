import sympy as sp

# Define symbolic variables
Edge_a, Edge_b = sp.symbols('Edge_a Edge_b')
a = Edge_a
b = Edge_b

# The main logic is encapsulated in functions
def get_spectre_points_sympy(a, b):
    """
    Generate symbolic coordinates for the Spectre tile vertices.
    """
    sqrt3 = sp.sqrt(3)
    a_sqrt3_d2 = a * sqrt3 / 2
    a_d2 = a / 2
    b_sqrt3_d2 = b * sqrt3 / 2
    b_d2 = b / 2
    
    spectre_points = [
        (0, 0),
        (a, 0),
        (a + a_d2, -a_sqrt3_d2),
        (a + a_d2 + b_sqrt3_d2, -a_sqrt3_d2 + b_d2),
        (a + a_d2 + b_sqrt3_d2, -a_sqrt3_d2 + b + b_d2),
        (a + a + a_d2 + b_sqrt3_d2, -a_sqrt3_d2 + b + b_d2),
        (a + a + a + b_sqrt3_d2, b + b_d2),
        (a + a + a, b + b),
        (a + a + a - b_sqrt3_d2, b + b - b_d2),
        (a + a + a_d2 - b_sqrt3_d2, a_sqrt3_d2 + b + b - b_d2),
        (a + a_d2 - b_sqrt3_d2, a_sqrt3_d2 + b + b - b_d2),
        (a_d2 - b_sqrt3_d2, a_sqrt3_d2 + b + b - b_d2),
        (-b_sqrt3_d2, b + b - b_d2),
        (0, b)
    ]
    return sp.Matrix(spectre_points)

# Define symbolic matrices for transformations
IDENTITY = sp.Matrix([[1, 0, 0], [0, 1, 0]])

def trot_sympy(deg_angle):
    """
    Return a symbolic rotation matrix.
    """
    angle = sp.rad(deg_angle)
    c = sp.cos(angle)
    s = sp.sin(angle)
    return sp.Matrix([[c, -s, 0], [s, c, 0]])

def mul_sympy(A, B):
    """
    Symbolic matrix multiplication for affine transformations.
    """
    AB = sp.Matrix(A)
    AB[:, :2] = A[:, :2] * B[:, :2]
    AB[:, 2] = A[:, :2] * B[:, 2] + A[:, 2]
    return AB

# Symbolic representation of the main classes and logic
class Tile:
    def __init__(self, label, quad):
        self.label = label
        self.quad = quad
    
    def forEachTile(self, doProc, tile_transformation=IDENTITY):
        return doProc(tile_transformation, self.label)

class MetaTile:
    def __init__(self, tiles=[], transformations=[], quad=None):
        self.tiles = tiles
        self.transformations = transformations
        self.quad = quad

    def forEachTile(self, doProc, transformation=IDENTITY):
        for tile, trsf in zip(self.tiles, self.transformations):
            tile.forEachTile(doProc, mul_sympy(transformation, trsf))


# Corrected function definition
def buildSpectreBase_sympy(spectre_points_all, rotation=30):
    """
    Build the base symbolic tiles.
    """
    # The quad_base variable from the original function is now defined here
    quad_base = sp.Matrix([spectre_points_all[3, :], spectre_points_all[5, :], spectre_points_all[7, :], spectre_points_all[11, :]])
    
    tiles = {
        label: Tile(label, quad_base) 
        for label in ["Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]
    }
    
    # Define symbolic transformation for the Gamma tile
    gamma2_trans = mul_sympy(
        sp.Matrix([[1, 0, spectre_points_all[8, 0]], [0, 1, spectre_points_all[8, 1]]]),
        trot_sympy(rotation)
    )
    
    # The quad for Gamma is the same as the others
    gamma_quad = quad_base 
    tiles["Gamma"] = MetaTile(
        tiles=[Tile("Gamma1", gamma_quad), Tile("Gamma2", gamma_quad)],
        transformations=[IDENTITY.copy(), gamma2_trans],
        quad=gamma_quad
    )
    return tiles


def buildSupertiles_sympy(input_tiles):
    """
    Iteratively build supertiles using symbolic transformations.
    """
    quad = input_tiles["Delta"].quad
    total_angle = 0
    transformations = [IDENTITY.copy()]
    
    # We need to correctly handle the point transformations
    for _angle, _from, _to in ((60, 3, 1), (0, 2, 0), (60, 3, 1), (60, 3, 1), 
                               (0, 2, 0), (60, 3, 1), (-120, 3, 3)):
        if _angle != 0:
            total_angle += _angle
            rotation = trot_sympy(total_angle)
        
        ttrans = IDENTITY.copy()
        
        # 1. Represent points in homogeneous coordinates (add a 1 to the end)
        point_from = sp.Matrix([quad[_from, 0], quad[_from, 1], 1])
        point_to = sp.Matrix([quad[_to, 0], quad[_to, 1], 1])

        # 2. Perform the correct matrix-vector multiplication
        # The result of the multiplication will be a (2, 1) vector
        ttrans_vec = transformations[-1] * point_from - rotation * point_to
        
        # 3. Assign the translation vector to the transformation matrix
        ttrans[:, 2] = ttrans_vec
        
        transformations.append(mul_sympy(ttrans, rotation))

    R = sp.Matrix([[-1, 0, 0], [0, 1, 0]])
    transformations = [mul_sympy(R, trsf) for trsf in transformations]

    # Symbolic supertile quad points calculation
    super_quad_points = [
        (transformations[6] * sp.Matrix([quad[2, 0], quad[2, 1], 1]))[:2, 0],
        (transformations[5] * sp.Matrix([quad[1, 0], quad[1, 1], 1]))[:2, 0],
        (transformations[3] * sp.Matrix([quad[2, 0], quad[2, 1], 1]))[:2, 0],
        (transformations[0] * sp.Matrix([quad[1, 0], quad[1, 1], 1]))[:2, 0]
    ]
    super_quad = sp.Matrix(super_quad_points).T
    
    # ... (rest of the code remains the same)
    substitutions_map = {
        "Gamma": ("Pi", "Delta", None, "Theta", "Sigma", "Xi", "Phi", "Gamma"),
        "Delta": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
        "Theta": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
        "Lambda": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
        "Xi": ("Psi", "Delta", "Pi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
        "Pi": ("Psi", "Delta", "Xi", "Phi", "Sigma", "Psi", "Phi", "Gamma"),
        "Sigma": ("Xi", "Delta", "Xi", "Phi", "Sigma", "Pi", "Lambda", "Gamma"),
        "Phi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Pi", "Phi", "Gamma"),
        "Psi": ("Psi", "Delta", "Psi", "Phi", "Sigma", "Psi", "Phi", "Gamma")
    }

    new_tiles = {}
    for label, substitutions in substitutions_map.items():
        sub_tiles = [input_tiles[subst] for subst in substitutions if subst]
        sub_transformations = [trsf for subst, trsf in zip(substitutions, transformations) if subst]
        new_tiles[label] = MetaTile(
            tiles=sub_tiles,
            transformations=sub_transformations,
            quad=super_quad
        )
    return new_tiles

# Example usage to demonstrate a single step


# Corrected main execution block
SPECTRE_POINTS_SYM = get_spectre_points_sympy(Edge_a, Edge_b)
SPECTRE_QUAD_SYM = sp.Matrix([SPECTRE_POINTS_SYM[3, :], SPECTRE_POINTS_SYM[5, :], SPECTRE_POINTS_SYM[7, :], SPECTRE_POINTS_SYM[11, :]])

# Pass the full points matrix, not the quad, to the function
base_tiles_sympy = buildSpectreBase_sympy(SPECTRE_POINTS_SYM)

# The rest of the code should now work without the IndexError
first_super_tiles_sympy = buildSupertiles_sympy(base_tiles_sympy)
print(first_super_tiles_sympy["Delta"].transformations[0])

all_tiles_info = []
def collect_tiles(tile_transformation, label):
    global all_tiles_info
    all_tiles_info.append({'label': label, 'transformation': tile_transformation})

first_super_tiles_sympy["Delta"].forEachTile(collect_tiles)
print(all_tiles_info)

# Start of the LaTeX document
latex_output = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[a4paper, margin=1in]{geometry}
\begin{document}

\title{Symbolic Transformations of Einstein Tiles}
\date{}
\maketitle

This document contains the LaTeX representations of the symbolic transformation matrices for the first iteration of the Einstein tiles. These matrices describe the rotation and translation of each sub-tile within the main "Delta" supertile. The transformations are expressed in terms of the symbolic edge lengths, \textbf{Edge\_a} and \textbf{Edge\_b}.

"""

# Iterate through the list and convert each matrix to LaTeX
for tile_info in all_tiles_info:
    label = tile_info['label']
    transformation_matrix = tile_info['transformation']
    
    # Use sympy.latex() to convert the matrix to LaTeX code
    latex_matrix = sp.latex(transformation_matrix, mat_str='pmatrix')
    
    latex_output += f"\\section*{{Tile: {label}}}"
    latex_output += f"\\begin{{equation*}}\n"
    latex_output += latex_matrix + "\n"
    latex_output += f"\\end{{equation*}}\n"
    latex_output += r"\vspace{0.5cm}" + "\n\n"

# End of the LaTeX document
latex_output += r"""
\end{document}
"""

print(latex_output)
tmp = '/tmp/einsteintile.tex'
open(tmp,'wb').write(latex_output.encode('utf-8'))
import subprocess
subprocess.check_call(['pdflatex', '--output-format', 'pdf', '--output-directory','/tmp', tmp])