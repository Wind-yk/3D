from math import isclose
from numpy.linalg import inv
from numpy import matrix, identity, sin, cos, pi, asmatrix, sqrt
from typing import Union # this shouldn't be necessary for > Python 3.9

# Project packages
from packages.point import Point
from packages.display import Display


# TODO: add setter for each point of vertices
class Mesh:
    """
    This class will handle a geometric body and
    send it to the Display class for render.
    """
    # ------------------------- internal methods ------------------------- #
    def __init__(
        self, 
        vertices: Union[list, matrix], 
        edges: 'list[int]', 
        center: Union[Point, float, int, list, tuple], 
        angle: Union[Point, float, int, list, tuple], 
        scale: Union[Point, float, int, list, tuple], 
        color: str='b'
    ):
        self.vertices = vertices # matrix of shape 4×|V|
        self.edges = edges       # need discussion
        self.center = center
        self.angle = angle
        self.scale = scale

        self.transform_matrix = identity(4)  # identity matrix of size 4×4
        temp = sqrt(2)/2
        self.camera = matrix([
            [ temp, temp, 0, 1],
            [-temp, temp, 0, 0],
            [    0,    0, 1, 0],
            [    0,    0, 0, 1]
        ])

        self.focal = matrix([
            [5, 0, 0, 0], # f 0 0 0
            [0, 5, 0, 0], # 0 f 0 0
            [0, 0, 1, 0], # 0 0 1 0
        ])
        self.applyTransform(center, angle, scale)
        self._transform_matrix_backup = self.transform_matrix

        self.show = True
        self.color = color


    # TODO: change the assert to exception
    def _scale_matrix(self, scale: Union[Point, float, int, list, tuple]) -> matrix:
        """
        Get the matrix that multiplies all the components by a factor of `s`.

        # Parameters
            - `s` (float): factor of product

        # Output:
            - `scale_matrix` (matrix): 4×4 matrix
        """
        if isinstance(scale, (tuple, list)):
            assert all(scale)  # check all values are non-zero
            x, y, z = scale
        elif isinstance(scale, (float, int)):
            assert not isclose(scale, 0)
            x = y = z = scale
        else:
            raise TypeError("Invalid scale.")
        
        scale_matrix = matrix([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ])
        self.scale *= [x, y, z]
        return scale_matrix


    def _shift_matrix(self, shift: Union[Point, list, tuple]) -> matrix:
        """
        Get the matrix that shifts all components by the vector `shift`.

        # Parameters
            - `shift` (Point): represents the vector of shift.
        
        # Output:
            - `shift_matrix` (matrix): 4×4 matrix
        """
        x, y, z = shift
        shift_matrix = matrix([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])
        self.center += shift
        return shift_matrix


    # TODO: change the assert to exception
    def _rotation_matrix(self, rotation: Union[Point, list, tuple]) -> matrix:
        """
        Get the matrix for the rotation.

        # Parameters
            - `rotation` (list|tuple): list-like of (yaw, pitch, roll).

        # Returns
            - `rotation_matrix` (matrix): 4×4 matrix

        https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
        """
        assert all(-2*pi <= angle < 2*pi for angle in rotation)

        alfa, beta, gamma = rotation
        c_a, c_b, c_c = cos(alfa), cos(beta), cos(gamma)
        s_a, s_b, s_c = sin(alfa), sin(beta), sin(gamma)

        rotation_matrix = matrix([
            [c_b*c_c, s_a*s_b*c_c - c_a*s_c, c_a*s_b*c_c + s_a*s_c, 0],
            [c_b*s_c, s_a*s_b*s_c + c_a*c_c, c_a*s_b*s_a - s_a*c_c, 0],
            [   -s_b,               s_a*c_b,               c_a*c_b, 0],
            [      0,                     0,                     0, 1]
        ])

        self.angle += rotation
        return rotation_matrix


    # TODO: add camera as parameter
    def _to2D(self) -> matrix:
        """
        Return the vertices mapped to 2D.
        """
        mapped_points = self.focal @ inv(self.camera) @ self.transform_matrix @ self.vertices
        return mapped_points[:2, :] / mapped_points[2,:]


    # ------------------------- properties ------------------------- # 
    @property
    def vertices(self):
        return self._vertices

    # TODO: change assert to exception
    # TODO: change the all equal to 1 -> allclose
    @vertices.setter
    def vertices(self, values: Union[matrix, list]):
        if not isinstance(values, matrix):
            values = asmatrix(values)

        if values.shape[0] != 4:         # the nº rows is not 4...
            assert values.shape[1] == 4  # ensure that it will have 4 rows after transpose
            values = values.T

        if not (values[3,:] == 1).all():
            assert values.shape[1] == 4  # ensure that it will have 4 rows after transpose
            values = values.T

        self._vertices = values


    @property
    def edges(self) -> list:
        return self._edges

    @edges.setter
    def edges(self, values: list): 
        self._edges = values

    
    @property
    def center(self) -> Point:
        return self._center

    @center.setter
    def center(self, center: Union[Point, float, int, list, tuple]):
        if isinstance(center, Point):
            self._center = center
        elif isinstance(center, (int, float)):
            self._center = Point(center, center, center)
        elif isinstance(center, (list, tuple)):
            self._center = Point(*center)
        else:
            raise TypeError("center must be set using one of: float, int, list, tuple, Point.")


    @property
    def angle(self) -> Point:
        return self._angle

    @angle.setter
    def angle(self, angle: Union[Point, float, int, list, tuple]):
        if isinstance(angle, Point):
            self._angle = angle
        elif isinstance(angle, (int, float)):
            self._angle = Point(angle, angle, angle)
        elif isinstance(angle, (list, tuple)):
            self._angle = Point(*angle)
        else:
            raise TypeError("angle must be set using one of: float, int, list, tuple, Point.")


    @property
    def scale(self) -> Point:
        return self._scale

    @scale.setter
    def scale(self, scale: Union[Point, float, int, list, tuple]):
        if isinstance(scale, Point):
            self._scale = scale
        if isinstance(scale, (int, float)):
            self._scale = Point(scale, scale,scale)
        elif isinstance(scale, (list, tuple, Point)):
            self._scale = Point(*scale)  # [v*s for v,s in zip(values, self._scale)]
        else:
            raise TypeError("scale must be set using one of: float, int, list, tuple, Point.")


    @property
    def show(self) -> bool:
        return self._show

    @show.setter
    def show(self, value:bool): 
        self._show = value


    @property
    def transform_matrix(self) -> matrix:
        return self._transform_matrix

    @transform_matrix.setter
    def transform_matrix(self, values: matrix): 
        self._transform_matrix = values


    @property
    def transform_matrix_backup(self) -> matrix:
        return self._transform_matrix_backup

    @transform_matrix_backup.setter
    def transform_matrix_backup(self, values: matrix): 
        self._transform_matrix_backup = values


    @property
    def color(self) -> str:
        return self._color

    # TODO: check if the color is valid
    @color.setter
    def color(self, value: str):
        self._color = value


    # ------------------------- methods ------------------------- #
    def send2render(self, display: Display) -> None:
        """
        Send the actual geometric body to render.
        """
        display.add_mesh(self)


    def toFBX(self, path: str, force: bool=False):
        """
        Save as fbx file.
        """
        pass

    
    # TODO: change assert to exception
    # TODO: dynamic mapped point instead of calculating on-line
    def get2DVertex(self, i):
        """Given index `i`, return the `i`th mapped point."""
        assert isinstance(i, int)
        return self._2DVertices[:,i]


    # TODO: change assert to exception
    def getVertex(self, i):
        """Given index `i`, return the i'th vertex."""
        assert isinstance(i, int)
        return self.vertices[:,i]


    def reset(self) -> None:
        """Reset to the initial transformation."""
        self.transform_matrix = self.transform_matrix_backup


    def disable(self) -> None:
        """Hide the geometric body."""
        self.show = False

    
    def enable(self) -> None:
        """Display the geometric body."""
        self.show = True


    # TODO: update the class variables and apply the changes (after reviewing that the values are correct)
    # TODO: so to automatically update the transformation matrix and the 2D vertex,
    # TODO: instead of calculating them one by one.
    def applyTransform(
        self, 
        center: Union[Point, float, int, list, tuple] = 0,
        angle: Union[Point, float, int, list, tuple] = 0,
        scale: Union[Point, float, int, list, tuple] = 1.
    ) -> None:
        """
        Update the tranform matrix. First shift, then rotate and at the end scale.
        
        # Parameters
            - `center` (Point): for translation
            - `angle` (list | tuple): 3-length in radians (yaw, pitch, roll)
            - `scale` (float): for scale

        https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
        """
        shift_matrix = self._shift_matrix(center)
        rotation_matrix = self._rotation_matrix(angle)
        scale_matrix = self._scale_matrix(scale)
        self.transform_matrix = scale_matrix @ rotation_matrix @ shift_matrix @ self.transform_matrix
        self._2DVertices = self._to2D()

