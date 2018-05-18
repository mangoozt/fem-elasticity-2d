from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
import numpy as np
from flatutils.graphic import apply_displacement


def create_shader(shader_type, source):
    # Создаем пустой объект шейдера
    shader = glCreateShader(shader_type)
    # Привязываем текст шейдера к пустому объекту шейдера
    glShaderSource(shader, source)
    # Компилируем шейдер
    glCompileShader(shader)
    # Возвращаем созданный шейдер
    return shader


MAXW = 800
MAXH = 700


def show_results_nodal(x, y, elements, a, ux=None, uy=None, multiplier=1, mesh=True):
    # add displacements to nodes' coordinates
    if not ((ux is None) | (uy is None)):
        _x, _y = x, y
        x, y = apply_displacement(x, y, ux, uy, multiplier)

    a = np.array(a)
    x = np.array(x)
    y = np.array(y)
    ymin = y.min()
    xmin = x.min()
    w = x.max() - xmin
    h = y.max() - ymin

    scale = min(MAXW / w, MAXH / h)

    width = int(w * scale)
    height = int(h * scale)

    def float_size(n=1):
        return sizeof(ctypes.c_float) * n

    def pointer_offset(n=0):
        return ctypes.c_void_p(float_size(n))

    def draw():
        glClear(GL_COLOR_BUFFER_BIT)  # Очищаем экран и заливаем серым цветом

        vertexPositions.bind()
        indexPositions.bind()

        glEnableVertexAttribArray(glGetAttribLocation(shader, 'position'))
        glVertexAttribPointer(glGetAttribLocation(shader, 'position'), 2, GL_FLOAT, False, float_size(3),
                              pointer_offset(0))
        glEnableVertexAttribArray(glGetAttribLocation(shader, 'value'))
        glVertexAttribPointer(glGetAttribLocation(shader, 'value'), 1, GL_FLOAT, False, float_size(3),
                              pointer_offset(2))

        glUseProgram(shader)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawElements(GL_TRIANGLES, len(elements) * 3, GL_UNSIGNED_INT, None)
        glDisable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        glDisable(GL_POLYGON_OFFSET_FILL)
        glUseProgram(white_shader)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        vertexPositions.bind()
        indexPositions.bind()
        glEnableVertexAttribArray(glGetAttribLocation(shader, 'position'))
        glVertexAttribPointer(glGetAttribLocation(shader, 'position'), 2, GL_FLOAT, False, float_size(3),
                              pointer_offset(0))
        glEnableVertexAttribArray(glGetAttribLocation(shader, 'value'))
        glVertexAttribPointer(glGetAttribLocation(shader, 'value'), 1, GL_FLOAT, False, float_size(3),
                              pointer_offset(2))
        glDrawElements(GL_TRIANGLES, len(elements) * 3, GL_UNSIGNED_INT, None)
        glutSwapBuffers()  # Выводим все нарисованное в памяти на экран

    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(50, 50)
    glutInit(sys.argv)
    glutCreateWindow(b"Solution")
    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glClearColor(0.2, 0.2, 0.2, 1)

    vertex_shader = shaders.compileShader("""
#version 150 core
in vec2 position;
in float value;
out float Val;
void main(){
    Val=value;
    gl_Position = vec4(position, 0.0, 1.0);
}""", GL_VERTEX_SHADER)
    # Определяет цвет каждого фрагмента как "смешанный" цвет его вершин
    fragment_shader = shaders.compileShader("""
#version 150 core

float colormap_red(float x) {
    if (x < 0.7) {
        return 4.0 * x - 1.5;
    } else {
        return -4.0 * x + 4.5;
    }
}

float colormap_green(float x) {
    if (x < 0.5) {
        return 4.0 * x - 0.5;
    } else {
        return -4.0 * x + 3.5;
    }
}

float colormap_blue(float x) {
    if (x < 0.3) {
       return 4.0 * x + 0.5;
    } else {
       return -4.0 * x + 2.5;
    }
}

vec4 colormap(float x) {
    float r = clamp(colormap_red(x), 0.0, 1.0);
    float g = clamp(colormap_green(x), 0.0, 1.0);
    float b = clamp(colormap_blue(x), 0.0, 1.0);
    return vec4(r, g, b, 1.0);
}
in float Val;
void main()
{
    gl_FragColor = colormap(Val);
}
""", GL_FRAGMENT_SHADER)
    # White coloring

    white_fragment_shader = shaders.compileShader("""
#version 150 core

void main()
{
    gl_FragColor = vec4(0,0,0,1);
}
""", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(vertex_shader, fragment_shader)
    white_shader = shaders.compileProgram(vertex_shader,white_fragment_shader)

    amin = a.min()
    arange_ = 1 / (a.max() - amin)
    print(y)
    print(h)
    vertices = np.array(
        [[2 * (x[i] - xmin - w / 2) / w, 2 * (y[i] - ymin - h / 2) / h, (a[i] - amin) * arange_] for i in
         range(len(x))],
        dtype='f')
    vertexPositions = vbo.VBO(vertices, usage=GL_STATIC_DRAW)
    print(vertices)
    elements = np.array(elements)
    indexPositions = vbo.VBO(elements, target=GL_ELEMENT_ARRAY_BUFFER, usage=GL_STATIC_DRAW)

    glutMainLoop()
