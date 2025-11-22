#!/usr/bin/env python3
"""
天体系统模拟器 - 主程序
基于Python的天体物理模拟系统，使用PyOpenGL进行3D渲染
"""

import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import json
from datetime import datetime
import threading
import time

# 导入自定义模块
from physics_engine import GravityEngine, CelestialBody
from renderer import OpenGLRenderer
from ui_manager import UIManager
from scene_manager import SceneManager
from config import *

class CelestialSimulator:
    """主模拟器类"""
    
    def __init__(self):
        """初始化模拟器"""
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.title = "天体系统模拟器"
        
        # 初始化Pygame
        pygame.init()
        pygame.display.set_caption(self.title)
        
        # 设置OpenGL显示模式
        self.screen = pygame.display.set_mode((self.width, self.height), 
                                            DOUBLEBUF | OPENGL | RESIZABLE)
        
        # 初始化OpenGL
        self.init_opengl()
        
        # 初始化组件
        self.renderer = OpenGLRenderer(self.width, self.height)
        # 默认开启真实物理半径显示（可切换），并设置一个合理的缩放倍率以便可见
        try:
            self.renderer.use_true_radii = True
            self.renderer.radius_scale_multiplier = 50.0
            print(f"Renderer: use_true_radii={self.renderer.use_true_radii} radius_scale_multiplier={self.renderer.radius_scale_multiplier}")
        except Exception:
            pass
        self.physics_engine = GravityEngine()
        self.ui_manager = UIManager(self.width, self.height)
        self.scene_manager = SceneManager()

        # 注册 UI 回调，将 UI 操作连接到模拟器方法或渲染器
        self.ui_manager.set_callbacks({
            'play_pause': self.toggle_pause,
            'reset': self.reset_camera,
            'clear': self.clear_all_bodies,
            'save': self.save_scene,
            'load': self.load_scene,
            'show_orbits': self.renderer.toggle_orbits,
            'show_labels': self.renderer.toggle_labels,
            'show_grid': self.renderer.toggle_grid,
            # 状态 getter，供 UI 用于显示当前开关状态
            'get_show_orbits': (lambda r=self.renderer: r.show_orbits),
            'get_show_labels': (lambda r=self.renderer: r.show_labels),
            'get_show_grid': (lambda r=self.renderer: r.show_grid),
            'set_time_speed': self.set_time_speed
        })
        
        # 模拟状态
        self.is_running = True
        self.is_simulation_paused = False
        self.time_speed = 1.0
        self.simulation_time = 0.0
        self.selected_body = None
        # 使用配置中的默认相机距离（以米为单位）
        self.camera_distance = DEFAULT_CAMERA_DISTANCE
        self.camera_rotation = [0.0, 0.0]
        
        # 天体列表
        self.celestial_bodies = dict()
        
        # 鼠标控制
        self.mouse_down = False
        self.mouse_button = 0
        self.last_mouse_pos = [0, 0]
        # 待处理的点击（在下一帧渲染时进行拾取，以确保矩阵正确）
        self.pending_click_pos = None
        
        # 性能监控
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0
        
        # 初始化默认场景
        self.load_default_scene()
        
    def init_opengl(self):
        """初始化OpenGL设置"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        # 启用法线归一化以避免非均匀缩放导致的光照问题
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        
        # 设置光照
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
        
        # 设置背景色
        glClearColor(0.02, 0.02, 0.05, 1.0)
        
        # 设置投影矩阵
        self.setup_projection()
        
    def setup_projection(self):
        """设置投影矩阵"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)
        
    def load_default_scene(self):
        """加载默认场景"""
        # 创建太阳系
        self.scene_manager.load_solar_system(self.celestial_bodies)
        # 将相机目标设置为系统质心，便于围绕系统旋转
        try:
            com = self.physics_engine.find_center_of_mass(self.celestial_bodies)
            if com is not None:
                self.renderer.camera_target = com
        except Exception:
            pass
        
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.is_running = False
                
            elif event.type == VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), 
                                                    DOUBLEBUF | OPENGL | RESIZABLE)
                self.setup_projection()
                self.renderer.resize(self.width, self.height)
                self.ui_manager.resize(self.width, self.height)
                
            elif event.type == MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.mouse_button = event.button
                self.last_mouse_pos = event.pos
                # print(f"MOUSEBUTTONDOWN button={event.button} pos={event.pos}")
                # 处理滚轮（按钮4/5）用于缩放相机距离
                if event.button == 4:  # 滚轮上
                    self.camera_distance = max(1e3, self.camera_distance * 0.9)
                    print(f"wheel up: camera_distance={self.camera_distance}")
                elif event.button == 5:  # 滚轮下
                    self.camera_distance = min(1e14, self.camera_distance * 1.1)
                    print(f"wheel down: camera_distance={self.camera_distance}")
                
                if event.button == 1:  # 左键
                    # 延迟拾取到下一渲染帧（此时 OpenGL 矩阵已设置）
                    self.pending_click_pos = event.pos
                        
            elif event.type == MOUSEBUTTONUP:
                self.mouse_down = False
                
            elif event.type == MOUSEMOTION:
                if self.mouse_down:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    # print(f"MOUSEMOTION dx={dx} dy={dy} button={self.mouse_button}")
                    
                    if self.mouse_button == 1:  # 左键 - 旋转相机
                        self.camera_rotation[0] += dy * 0.5
                        self.camera_rotation[1] += dx * 0.5
                        self.camera_rotation[0] = max(-85, min(85, self.camera_rotation[0]))
                        
                    elif self.mouse_button == 3:  # 右键 - 平移相机目标（改变旋转中心）
                        # 将屏幕偏移转换为世界偏移（近似）
                        # 偏移比例与相机距离成正比
                        factor = self.camera_distance * 0.002
                        right = np.array([math.sin(math.radians(self.camera_rotation[1]-90)), 0.0, math.cos(math.radians(self.camera_rotation[1]-90))])
                        up = np.array([0.0, 1.0, 0.0])
                        move = -dx * factor * right + dy * factor * up
                        try:
                            self.renderer.camera_target = self.renderer.camera_target + move
                        except Exception:
                            self.renderer.camera_target = np.array(self.renderer.camera_target) + move
                        
                    self.last_mouse_pos = event.pos
                    
                # 鼠标滚轮缩放
                if event.buttons[1]:  # 中键
                    dz = event.rel[1]
                    self.camera_distance += dz * 0.5
                    self.camera_distance = max(10, min(5000, self.camera_distance))
                    
            elif event.type == KEYDOWN:
                print(f"KEYDOWN key={event.key} unicode={getattr(event, 'unicode', None)}")
                # 支持使用字符来检测 '[' ']'，兼容不同键盘/系统
                if getattr(event, 'unicode', None) == '[':
                    try:
                        self.renderer.change_scale(0.5)
                        print(f"render scale multiplier: {self.renderer.scale_multiplier}")
                    except Exception:
                        pass
                    continue
                elif getattr(event, 'unicode', None) == ']':
                    try:
                        self.renderer.change_scale(2.0)
                        print(f"render scale multiplier: {self.renderer.scale_multiplier}")
                    except Exception:
                        pass
                    continue
                print(f"KEYDOWN key={event.key}")
                self.handle_keydown(event)
                
            # UI事件处理
            self.ui_manager.handle_event(event)
            
    def handle_keydown(self, event):
        """处理键盘按键"""
        if event.key == K_SPACE:
            self.is_simulation_paused = not self.is_simulation_paused
            
        elif event.key == K_r:
            self.reset_camera()
            
        elif event.key == K_c:
            self.clear_all_bodies()
            
        elif event.key == K_s:
            self.save_scene()
            
        elif event.key == K_l:
            self.load_scene()
            
        elif event.key == K_1:
            self.load_solar_system()
            
        elif event.key == K_2:
            self.load_binary_system()
            
        elif event.key == K_3:
            self.load_random_system()
            
        elif event.key == K_PLUS or event.key == K_EQUALS:
            self.time_speed = min(100.0, self.time_speed * 2)
            
        elif event.key == K_MINUS:
            self.time_speed = max(0.1, self.time_speed * 0.5)
            
        elif event.key == K_ESCAPE:
            self.is_running = False
        elif event.key == K_LEFTBRACKET:  # '[' 减小渲染尺度
            try:
                self.renderer.change_scale(0.5)
                print(f"render scale multiplier: {self.renderer.scale_multiplier}")
            except Exception:
                pass
        elif event.key == K_RIGHTBRACKET:  # ']' 增大渲染尺度
            try:
                self.renderer.change_scale(2.0)
                print(f"render scale multiplier: {self.renderer.scale_multiplier}")
            except Exception:
                pass
        # 切换真实物理半径显示（T），并用 ',' '.' 调整半径缩放倍率
        elif event.key == K_t:
            try:
                self.renderer.use_true_radii = not self.renderer.use_true_radii
                print(f"use_true_radii -> {self.renderer.use_true_radii}")
            except Exception:
                pass
        elif event.key == K_COMMA:  # 缩小半径缩放倍数
            try:
                self.renderer.radius_scale_multiplier = max(0.001, self.renderer.radius_scale_multiplier * 0.5)
                print(f"radius_scale_multiplier -> {self.renderer.radius_scale_multiplier}")
            except Exception:
                pass
        elif event.key == K_PERIOD:  # 增大半径缩放倍数
            try:
                self.renderer.radius_scale_multiplier = self.renderer.radius_scale_multiplier * 2.0
                print(f"radius_scale_multiplier -> {self.renderer.radius_scale_multiplier}")
            except Exception:
                pass
            
    def reset_camera(self):
        """重置相机位置"""
        self.camera_rotation = [0.0, 0.0]
        self.camera_distance = 500.0
        self.renderer.camera_pos = [0.0, 0.0, 500.0]

    def toggle_pause(self):
        """由 UI 回调触发：切换模拟暂停状态并同步 UI 标志"""
        self.is_simulation_paused = not self.is_simulation_paused
        try:
            self.ui_manager.is_simulation_paused = self.is_simulation_paused
        except Exception:
            pass

    def set_time_speed(self, speed: float):
        """由 UI 滑块回调触发：设置时间速度"""
        try:
            self.time_speed = float(speed)
        except Exception:
            pass
        
    def clear_all_bodies(self):
        """清空所有天体"""
        self.celestial_bodies.clear()
        self.selected_body = None
        
    def update_physics(self, dt):
        """更新物理模拟"""
        if not self.is_simulation_paused and self.celestial_bodies:
            # 计算时间步长（考虑时间加速）
            time_step = dt * self.time_speed * 86400.0  # dt 已为秒
            
            # 更新物理
            self.physics_engine.update_positions(self.celestial_bodies, time_step)
            
            # 更新模拟时间
            self.simulation_time += time_step
            
    def render(self):
        """渲染场景"""
        # 清除缓冲区
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置相机
        # 传入以米为单位的相机距离，渲染器会应用 RENDER_SCALE
        self.renderer.setup_camera(self.camera_distance, self.camera_rotation)
        # 如有待处理点击，则在相机/矩阵已设置的情况下执行拾取
        if getattr(self, 'pending_click_pos', None) is not None:
            selected_body = self.renderer.pick_body(self.pending_click_pos, self.celestial_bodies,
                                                   self.camera_distance, self.camera_rotation)
            if selected_body:
                self.selected_body = selected_body
                try:
                    print(f"SELECTED: {selected_body.name}")
                except Exception:
                    print("SELECTED a body")
            else:
                print("SELECTED: none")
            self.pending_click_pos = None
        
        # 渲染天体
        self.renderer.render_celestial_bodies(self.celestial_bodies, self.selected_body)
        
        # 渲染星空背景
        self.renderer.render_star_field()
        
        # 生成世界坐标标签（在 3D 渲染完成且矩阵就绪时）并传给 UI 渲染
        world_labels = None
        try:
            if self.renderer.show_labels:
                world_labels = []
                for body_key, body in self.celestial_bodies.items():
                    # 使用与渲染一致的缩放单位
                    scaled_pos = body.position * RENDER_SCALE * self.renderer.scale_multiplier
                    winx, winy, winz = self.renderer.world_to_screen(scaled_pos)
                    if winx is not None:
                        # UI 的坐标系在 draw_text 中假设 y 向下，从 0 到 height
                        screen_x = int(winx)
                        screen_y = int(self.height - winy)
                        world_labels.append((body.name, screen_x, screen_y))
                # 调试打印：显示标签数量与前几个样例
                try:
                    print(f"world_labels count={len(world_labels)} samples={world_labels[:6]}")
                except Exception:
                    pass
        except Exception:
            world_labels = None

        # 渲染UI（传入屏幕标签）
        self.ui_manager.render(self.celestial_bodies, self.selected_body, 
                             self.simulation_time, self.time_speed, self.fps, world_labels)
        
        # 交换缓冲区
        pygame.display.flip()
        
    def update_fps(self):
        """更新FPS计数"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
            
    def save_scene(self):
        """保存当前场景"""
        scene_data = {
            'timestamp': datetime.now().isoformat(),
            'bodies': []
        }
        
        for body in self.celestial_bodies:
            body_data = {
                'name': body.name,
                'type': body.type,
                'mass': body.mass,
                'radius': body.radius,
                'position': [body.position.x, body.position.y, body.position.z],
                'velocity': [body.velocity.x, body.velocity.y, body.velocity.z],
                'color': body.color
            }
            scene_data['bodies'].append(body_data)
            
        filename = f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, indent=2, ensure_ascii=False)
            
        print(f"场景已保存到: {filename}")
        
    def load_scene(self):
        """加载场景"""
        # 这里可以实现文件选择对话框
        filename = "scene_20231201_120000.json"  # 示例文件名
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
                
            self.clear_all_bodies()
            
            for body_data in scene_data['bodies']:
                body = CelestialBody(
                    name=body_data['name'],
                    type=body_data['type'],
                    mass=body_data['mass'],
                    radius=body_data['radius'],
                    position=body_data['position'],
                    velocity=body_data['velocity'],
                    color=body_data['color']
                )
                self.celestial_bodies.append(body)
                
            print(f"场景已从 {filename} 加载")
            
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
            
    def load_solar_system(self):
        """加载太阳系"""
        self.clear_all_bodies()
        self.scene_manager.load_solar_system(self.celestial_bodies)
        
    def load_binary_system(self):
        """加载双星系统"""
        self.clear_all_bodies()
        self.scene_manager.load_binary_system(self.celestial_bodies)
        
    def load_random_system(self):
        """加载随机系统"""
        self.clear_all_bodies()
        self.scene_manager.load_random_system(self.celestial_bodies)
        
    def run(self):
        """主循环"""
        clock = pygame.time.Clock()
        
        while self.is_running:
            # 处理事件
            self.handle_events()
            
            # 更新物理
            dt = clock.tick(60) / 1000.0  # 转换为秒
            self.update_physics(dt)
            
            # 渲染
            self.render()
            
            # 更新FPS
            self.update_fps()
            
        # 清理
        pygame.quit()
        sys.exit()
        
if __name__ == "__main__":
    # 创建并运行模拟器
    simulator = CelestialSimulator()
    simulator.run()