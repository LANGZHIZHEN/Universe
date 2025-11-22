"""
OpenGL渲染器
处理3D场景的渲染，包括天体、轨道、星空等
"""

import numpy as np
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from PIL import Image
import io
from config import RENDER_SCALE

class OpenGLRenderer:
    """OpenGL渲染器类"""
    
    def __init__(self, width: int, height: int):
        """初始化渲染器"""
        self.width = width
        self.height = height
        
        # 相机参数
        self.camera_pos = np.array([0.0, 0.0, 500.0])
        self.camera_target = np.array([0.0, 0.0, 0.0])
        self.camera_up = np.array([0.0, 1.0, 0.0])
        
        # 渲染选项
        self.show_orbits = True
        self.show_labels = True
        self.show_trails = True
        self.show_grid = False
        
        # 光照
        self.light_pos = np.array([0.0, 0.0, 0.0, 1.0])  # 点光源在中心
        
        # 星空背景
        # 渲染时的动态缩放倍率（在运行时可调整，便于调试显示尺度）
        self.scale_multiplier = 1.0

        # 最小可见/可点击半径（渲染单位），用于确保小天体可见并且拾取一致
        self.min_display_radius = 0.3

        # 行星半径显示控制：是否使用真实物理半径（经过渲染缩放），以及针对半径的额外放大倍数
        # 当 use_true_radii=False 时，仍会对过小的物体应用 min_display_radius
        self.use_true_radii = True
        self.radius_scale_multiplier = 1.0

        # 拾取屏幕空间回退的像素阈值
        self.pick_pixel_threshold = 20.0

        # star_field 存储为单位方向向量（在渲染时按照摄像机位置放置在远处）
        self.star_field = self.generate_star_field(5000)
        
        # 显示列表缓存
        self.sphere_display_list = None
        glutInit()
        
    def generate_star_field(self, num_stars: int) -> np.ndarray:
        """生成星空背景"""
        # 生成随机方向矢量并归一化，这样渲染时可将它们放到相机远处形成背景天穹
        v = np.random.randn(num_stars, 3)
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        dirs = v / norms
        return dirs
        
    def setup_camera(self, distance: float, rotation: list):
        """设置相机位置和方向"""
        # 根据旋转角度计算相机位置
        phi = math.radians(rotation[0])  # 垂直旋转
        theta = math.radians(rotation[1])  # 水平旋转
        # 在计算相机位置/视图时使用渲染缩放（包含运行时倍率）
        scaled_distance = distance * RENDER_SCALE * self.scale_multiplier

        # 计算相对于目标的偏移向量，再将偏移加到目标位置上
        offset_x = scaled_distance * math.cos(phi) * math.sin(theta)
        offset_y = scaled_distance * math.sin(phi)
        offset_z = scaled_distance * math.cos(phi) * math.cos(theta)

        scaled_target = self.camera_target * RENDER_SCALE * self.scale_multiplier

        self.camera_pos[0] = scaled_target[0] + offset_x
        self.camera_pos[1] = scaled_target[1] + offset_y
        self.camera_pos[2] = scaled_target[2] + offset_z

        # 设置视图矩阵（使用已缩放的相机位置与目标）
        gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
              scaled_target[0], scaled_target[1], scaled_target[2],
              self.camera_up[0], self.camera_up[1], self.camera_up[2])
                  
    def render_celestial_bodies(self, bodies: dict, selected_body):
        """渲染天体"""
        for body_key, body in bodies.items():
            glPushMatrix()
            
            # 移动到天体位置
            scaled_pos = body.position * RENDER_SCALE * self.scale_multiplier
            glTranslatef(float(scaled_pos[0]), float(scaled_pos[1]), float(scaled_pos[2]))
            
            # 设置颜色
            glColor3f(*body.color)
            
            # 根据天体类型设置材质属性
            self.setup_material_properties(body)
            
            # 渲染天体
            if body.type == 'star':
                self.render_star(body)
            elif body.type == 'planet':
                self.render_planet(body)
            elif body.type == 'moon':
                self.render_moon(body)
            elif body.type == 'asteroid':
                self.render_asteroid(body)
                
            # 高亮选中的天体
            if body is selected_body:
                self.render_selection_highlight(body)
                
            glPopMatrix()
            
    def render_star(self, body):
        """渲染恒星"""
        # 恒星是光源，使用自发光材质
        glMaterialfv(GL_FRONT, GL_EMISSION, [body.color[0], body.color[1], body.color[2], 1.0])
        
        # 绘制恒星本体（根据当前半径模式选择显示半径）
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            r_draw = r_physical * self.radius_scale_multiplier
        else:
            r_draw = max(r_physical, self.min_display_radius)
        self.draw_sphere(r_draw)
        
        # 绘制光晕效果
        self.render_glow(body)
        
        # 重置发光材质
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        
    def render_planet(self, body):
        """渲染行星"""
        # 设置行星材质
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0], body.color[1], body.color[2], 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            r_draw = r_physical * self.radius_scale_multiplier
        else:
            r_draw = max(r_physical, self.min_display_radius)
        self.draw_sphere(r_draw)
        
        # 如果有大气层，渲染大气效果
        if hasattr(body, 'has_atmosphere') and body.has_atmosphere:
            self.render_atmosphere(body)
            
    def render_moon(self, body):
        """渲染卫星"""
        # 卫星材质较暗
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0]*0.8, body.color[1]*0.8, body.color[2]*0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 10.0)
        
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            r_draw = r_physical * self.radius_scale_multiplier
        else:
            r_draw = max(r_physical, self.min_display_radius)
        self.draw_sphere(r_draw)
        
    def render_asteroid(self, body):
        """渲染小行星"""
        # 小行星使用不规则形状
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.3, 0.2, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0], body.color[1], body.color[2], 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            r_draw = r_physical * self.radius_scale_multiplier
        else:
            r_draw = max(r_physical, self.min_display_radius)
        self.draw_irregular_shape(r_draw)
        
    def draw_sphere(self, radius: float, segments: int = 32):
        """绘制球体"""
        if self.sphere_display_list is None:
            self.sphere_display_list = glGenLists(1)
            glNewList(self.sphere_display_list, GL_COMPILE)
            
            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluSphere(quadric, 1.0, segments, segments)
            gluDeleteQuadric(quadric)
            
            glEndList()
            
        # 缩放球体到指定半径（保证最小可见尺寸）
        display_radius = max(radius, self.min_display_radius)
        glScalef(display_radius, display_radius, display_radius)
        glCallList(self.sphere_display_list)
        
    def draw_irregular_shape(self, base_radius: float):
        """绘制不规则形状（用于小行星）"""
        # 使用随机顶点创建不规则形状
        vertices = []
        faces = []
        
        # 生成顶点
        num_vertices = 20
        for i in range(num_vertices):
            theta = 2 * math.pi * i / num_vertices
            phi = math.pi * (i % 2)  # 交替上下
            
            # 添加随机性（base_radius 已为渲染单位）
            r = base_radius * (0.8 + 0.4 * np.random.random())
            
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.cos(phi)
            z = r * math.sin(phi) * math.sin(theta)
            
            vertices.append([x, y, z])
            
        # 生成面
        for i in range(num_vertices):
            next_i = (i + 1) % num_vertices
            
            # 连接到中心点形成三角形
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0)
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[next_i])
            glEnd()
            
    def render_glow(self, body):
        """渲染恒星的光晕效果"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # 多层光晕
        for i in range(3):
            alpha = 0.3 - i * 0.1
            size = body.radius * RENDER_SCALE * self.scale_multiplier * (2.0 + i * 0.5)

            glColor4f(body.color[0], body.color[1], body.color[2], alpha)
            glPushMatrix()
            glScalef(size, size, size)
            self.draw_sphere(1.0, 16)
            glPopMatrix()
            
        glDisable(GL_BLEND)
        
    def render_atmosphere(self, body):
        """渲染行星大气层"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 大气层颜色（偏蓝）
        glColor4f(0.5, 0.7, 1.0, 0.2)
        
        # 稍微放大一点
        atmosphere_radius = body.radius * 1.1 * RENDER_SCALE * self.scale_multiplier
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            base_r = r_physical * self.radius_scale_multiplier
        else:
            base_r = max(r_physical, self.min_display_radius)
        atmosphere_radius = base_r * 1.1
        glPushMatrix()
        glScalef(atmosphere_radius, atmosphere_radius, atmosphere_radius)
        self.draw_sphere(1.0, 32)
        glPopMatrix()
        
        glDisable(GL_BLEND)
        
    def render_selection_highlight(self, body):
        """渲染选中高亮"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # 绘制选中环
        glColor4f(1.0, 1.0, 0.0, 0.8)
        glLineWidth(3.0)
        
        glPushMatrix()
        r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
        if self.use_true_radii:
            r_display = max(r_physical * self.radius_scale_multiplier, self.min_display_radius)
        else:
            r_display = max(r_physical, self.min_display_radius)
        glScalef(r_display * 1.2, r_display * 1.2, r_display * 1.2)
        # 使用 GLU 四叉体以替代 GLUT 的 wire sphere，避免 GLUT 依赖导致的访问冲突
        quad = gluNewQuadric()
        gluQuadricDrawStyle(quad, GLU_LINE)
        gluSphere(quad, 1.0, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
    def render_orbits(self, bodies: list):
        """渲染轨道"""
        if not self.show_orbits:
            return
            
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for body_key, body in bodies.items():
            if len(body.trail) < 2:
                continue
                
            # 设置轨道颜色（半透明）
            glColor4f(body.color[0], body.color[1], body.color[2], 0.6)
            glLineWidth(2.0)
            
            # 绘制轨道线
            glBegin(GL_LINE_STRIP)
            for point in body.trail:
                glVertex3f(point[0] * RENDER_SCALE * self.scale_multiplier, point[1] * RENDER_SCALE * self.scale_multiplier, point[2] * RENDER_SCALE * self.scale_multiplier)
            glEnd()
            
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
    def render_star_field(self):
        """渲染星空背景"""
        glDisable(GL_LIGHTING)
        # 将星空绘制在非常远的球面上，始终位于相机远端，且不受深度测试影响
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        glColor3f(1.0, 1.0, 1.0)
        # 适当增大点大小以便在高缩放/高分辨率屏幕上可见
        glPointSize(2.5)

        # 远距离（米）设置为一个很大的值，渲染时会乘以 RENDER_SCALE 和 scale_multiplier
        far_distance_m = 1.0e13
        far_scaled = far_distance_m * RENDER_SCALE * self.scale_multiplier

        glBegin(GL_POINTS)
        for dir_vec in self.star_field:
            # 将星点放置在摄像机位置的远处方向上
            x = self.camera_pos[0] + float(dir_vec[0]) * far_scaled
            y = self.camera_pos[1] + float(dir_vec[1]) * far_scaled
            z = self.camera_pos[2] + float(dir_vec[2]) * far_scaled
            glVertex3f(x, y, z)
        glEnd()

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
    def render_grid(self):
        """渲染坐标网格"""
        if not self.show_grid:
            return
            
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.2, 0.2)
        
        grid_size = 1000
        grid_step = 100
        
        # XZ平面网格
        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1, grid_step):
            glVertex3f(i, 0, -grid_size)
            glVertex3f(i, 0, grid_size)
            glVertex3f(-grid_size, 0, i)
            glVertex3f(grid_size, 0, i)
        glEnd()
        
        glEnable(GL_LIGHTING)
        
    def setup_material_properties(self, body):
        """根据天体类型设置材质属性"""
        if body.type == 'star':
            # 恒星自发光
            glMaterialfv(GL_FRONT, GL_EMISSION, [body.color[0], body.color[1], body.color[2], 1.0])
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
            
        elif body.type == 'planet':
            # 行星有反射材质
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0], body.color[1], body.color[2], 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
            
        elif body.type == 'moon':
            # 卫星材质较暗
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0]*0.8, body.color[1]*0.8, body.color[2]*0.8, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 10.0)
            
        elif body.type == 'asteroid':
            # 小行星材质粗糙
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.3, 0.2, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [body.color[0], body.color[1], body.color[2], 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 0.0)
            
    def pick_body(self, mouse_pos: tuple, bodies: list, camera_distance: float, camera_rotation: list) -> object:
        """鼠标拾取天体"""
        # 使用 gluUnProject 从窗口坐标生成世界坐标射线（更精确）
        win_x = float(mouse_pos[0])
        # OpenGL 窗口 Y 与 Pygame Y 方向不同
        win_y = float(self.height - mouse_pos[1])

        # 获取当前矩阵与视口
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        # 近/远平面点（窗口坐标 z=0..1）
        try:
            near = gluUnProject(win_x, win_y, 0.0, model, proj, viewport)
            far = gluUnProject(win_x, win_y, 1.0, model, proj, viewport)
        except Exception:
            # 退回到简单方向向量方法
            ray_origin = self.camera_pos.copy()
            phi = math.radians(camera_rotation[0])
            theta = math.radians(camera_rotation[1])
            ray_direction = np.array([
                math.cos(phi) * math.sin(theta),
                math.sin(phi),
                math.cos(phi) * math.cos(theta)
            ])
            near = ray_origin
            far = ray_origin + ray_direction * 1.0

        ray_origin = np.array(near, dtype=np.float64)
        ray_dir = np.array(far, dtype=np.float64) - ray_origin
        ray_dir = ray_dir / np.linalg.norm(ray_dir)

        closest_body = None
        closest_t = float('inf')

        # 若启用详细调试，打印每个天体的相对参数
        debug = False

        for body_key, body in bodies.items():
            # 天体位置（渲染单位）
            body_pos = np.array(body.position * RENDER_SCALE * self.scale_multiplier, dtype=np.float64)

            # 求解射线与球体最短距离（射线参数 t）
            L = body_pos - ray_origin
            t_ca = np.dot(L, ray_dir)
            if t_ca < 0:
                # 球心在射线起点背后，仍需检查（射线从相机向外）
                pass

            d2 = np.dot(L, L) - t_ca * t_ca
            # 物理半径（渲染单位）
            r_physical = body.radius * RENDER_SCALE * self.scale_multiplier
            # 实际用于渲染与拾取的半径（至少为最小显示半径）
            r_display = max(r_physical, self.min_display_radius)
            if debug:
                try:
                    print(f"[pick-debug] body={getattr(body,'name',body_key)} pos={body_pos} r_physical={r_physical} r_display={r_display} t_ca={t_ca} d2={d2}")
                except Exception:
                    pass

            # 使用显示半径进行相交测试，这样可与屏幕上实际看到的球体一致
            if d2 <= r_display * r_display:
                # 计算距离到相交点的 t
                thc = math.sqrt(max(0.0, r_display * r_display - d2))
                t0 = t_ca - thc
                t1 = t_ca + thc
                t = t0 if t0 > 0 else t1
                if t > 0 and t < closest_t:
                    closest_t = t
                    closest_body = body
                    try:
                        print(f"[pick] hit body={body.name} r_display={r_display} r_physical={r_physical} t={t} d2={d2}")
                    except Exception:
                        pass

            # 如果射线测试没有命中任何天体，使用屏幕空间回退：将每个天体中心投影到窗口坐标并比较像素距离
            if closest_body is None:
                try:
                    mouse_win_x = win_x
                    mouse_win_y = win_y
                    pixel_threshold = self.pick_pixel_threshold  # 像素阈值，可通过属性调整

                    best_body = None
                    best_dist = float('inf')

                    for body_key, body in bodies.items():
                        body_pos = np.array(body.position * RENDER_SCALE * self.scale_multiplier, dtype=np.float64)
                        try:
                            proj_xy = gluProject(float(body_pos[0]), float(body_pos[1]), float(body_pos[2]), model, proj, viewport)
                            winx = proj_xy[0]
                            winy = proj_xy[1]
                            dx = winx - mouse_win_x
                            dy = winy - mouse_win_y
                            dist_px = math.hypot(dx, dy)
                            # print(f"[pick-fallback] body={getattr(body,'name',body_key)} win=({winx:.1f},{winy:.1f}) dist_px={dist_px:.2f}")
                            if dist_px < pixel_threshold and dist_px < best_dist:
                                best_dist = dist_px
                                best_body = body
                        except Exception:
                            pass

                    if best_body is not None:
                        print(f"[pick-fallback] selected body={getattr(best_body,'name','unknown')} dist_px={best_dist}")
                        closest_body = best_body
                except Exception:
                    pass

            return closest_body

        def world_to_screen(self, world_pos: np.ndarray) -> tuple:
            """将世界坐标（渲染单位）投影到窗口坐标，返回 (winx, winy, winz)。

            `world_pos` 应当是渲染单位（已经乘以 RENDER_SCALE 和 scale_multiplier）。
            """
            try:
                model = glGetDoublev(GL_MODELVIEW_MATRIX)
                proj = glGetDoublev(GL_PROJECTION_MATRIX)
                viewport = glGetIntegerv(GL_VIEWPORT)
                proj_xy = gluProject(float(world_pos[0]), float(world_pos[1]), float(world_pos[2]), model, proj, viewport)
                return (proj_xy[0], proj_xy[1], proj_xy[2])
            except Exception:
                return (None, None, None)
        
        
    def resize(self, width: int, height: int):
        """调整渲染器大小"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def change_scale(self, factor: float):
        """按比例调整运行时渲染缩放倍率并更新星空缓存。"""
        try:
            self.scale_multiplier *= factor
            # 更新星场以应用新的倍率
            self.star_field = self.generate_star_field(5000) * RENDER_SCALE * self.scale_multiplier
        except Exception:
            pass
        
    def toggle_orbits(self):
        """切换轨道显示"""
        self.show_orbits = not self.show_orbits
        
    def toggle_labels(self):
        """切换标签显示"""
        self.show_labels = not self.show_labels
        
    def toggle_trails(self):
        """切换轨迹显示"""
        self.show_trails = not self.show_trails
        
    def toggle_grid(self):
        """切换网格显示"""
        self.show_grid = not self.show_grid