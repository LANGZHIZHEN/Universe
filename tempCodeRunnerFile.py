"""
UI管理器
处理用户界面的渲染和交互
"""

import pygame
import numpy as np
from OpenGL.GL import *
import math
from OpenGL.GLU import gluOrtho2D

class UIManager:
    """UI管理器类"""
    
    def __init__(self, width: int, height: int):
        """初始化UI管理器"""
        self.width = width
        self.height = height
        
        # 字体
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 14)
        self.font_normal = pygame.font.Font(None, 16)
        self.font_large = pygame.font.Font(None, 20)
        
        # UI元素位置
        self.panel_width = 250
        self.panel_height = height
        
        # 控制面板状态
        self.show_control_panel = True
        self.show_info_panel = True
        
        # 颜色定义
        self.colors = {
            'background': (20, 30, 50, 200),
            'border': (0, 255, 255, 255),
            'text': (255, 255, 255, 255),
            'highlight': (255, 215, 0, 255),
            'warning': (255, 100, 100, 255),
            'success': (100, 255, 100, 255)
        }
        
        # 按钮状态
        self.buttons = {}
        self.sliders = {}
        
        # 输入框
        self.text_inputs = {}
        self.active_input = None
        
    def handle_event(self, event):
        """处理UI事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.KEYDOWN:
            self.handle_key_input(event)
            
    def handle_mouse_click(self, pos: tuple, button: int):
        """处理鼠标点击"""
        x, y = pos
        
        # 检查按钮点击
        for button_id, button_rect in self.buttons.items():
            if button_rect.collidepoint(x, y):
                self.on_button_click(button_id)
                
        # 检查滑块点击
        for slider_id, slider_data in self.sliders.items():
            if slider_data['rect'].collidepoint(x, y):
                self.on_slider_click(slider_id, x)
                
    def handle_key_input(self, event):
        """处理键盘输入"""
        if self.active_input and event.key:
            input_data = self.text_inputs[self.active_input]
            
            if event.key == pygame.K_BACKSPACE:
                input_data['text'] = input_data['text'][:-1]
            elif event.key == pygame.K_RETURN:
                self.active_input = None
            elif event.key < 256:
                input_data['text'] += event.unicode
                
    def on_button_click(self, button_id: str):
        """按钮点击处理"""
        if button_id == 'play_pause':
            self.toggle_simulation()
        elif button_id == 'reset':
            self.reset_simulation()
        elif button_id == 'clear':
            self.clear_scene()
        elif button_id == 'save':
            self.save_scene()
        elif button_id == 'load':
            self.load_scene()
        elif button_id == 'show_orbits':
            self.toggle_orbits()
        elif button_id == 'show_labels':
            self.toggle_labels()
        elif button_id == 'show_grid':
            self.toggle_grid()
            
    def on_slider_click(self, slider_id: str, x: int):
        """滑块点击处理"""
        if slider_id == 'time_speed':
            slider_data = self.sliders[slider_id]
            relative_x = x - slider_data['rect'].x
            percentage = max(0, min(1, relative_x / slider_data['rect'].width))
            time_speed = 0.1 + percentage * 99.9  # 0.1x 到 100x
            self.set_time_speed(time_speed)
            
    def render(self, bodies: list, selected_body, simulation_time: float, 
               time_speed: float, fps: int):
        """渲染UI"""
        # 切换到正交投影用于UI渲染
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 渲染控制面板
        if self.show_control_panel:
            self.render_control_panel(time_speed, fps)
            
        # 渲染信息面板
        if self.show_info_panel:
            self.render_info_panel(bodies, selected_body, simulation_time, fps)
            
        # 渲染状态栏
        self.render_status_bar(simulation_time, time_speed, fps)
        
        # 渲染工具提示
        self.render_tooltips()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def render_control_panel(self, time_speed: float, fps: int):
        """渲染控制面板"""
        x = 10
        y = 10
        width = self.panel_width
        height = 400
        
        # 面板背景
        self.draw_panel(x, y, width, height)
        
        # 标题
        self.draw_text("控制面板", x + 10, y + 10, self.colors['highlight'], self.font_large)
        
        current_y = y + 40
        
        # 播放/暂停按钮
        button_rect = pygame.Rect(x + 10, current_y, 100, 30)
        self.buttons['play_pause'] = button_rect
        self.draw_button(button_rect, "暂停" if not self.is_simulation_paused else "继续", 
                        self.colors['success'])
        current_y += 40
        
        # 重置按钮
        button_rect = pygame.Rect(x + 10, current_y, 100, 30)
        self.buttons['reset'] = button_rect
        self.draw_button(button_rect, "重置", self.colors['warning'])
        current_y += 40
        
        # 清空按钮
        button_rect = pygame.Rect(x + 10, current_y, 100, 30)
        self.buttons['clear'] = button_rect
        self.draw_button(button_rect, "清空", self.colors['warning'])
        current_y += 40
        
        # 时间速度滑块
        self.draw_text("时间流速", x + 10, current_y, self.colors['text'], self.font_normal)
        current_y += 25
        
        slider_rect = pygame.Rect(x + 10, current_y, width - 20, 20)
        self.sliders['time_speed'] = {'rect': slider_rect, 'value': time_speed}
        self.draw_slider(slider_rect, time_speed / 100.0)
        current_y += 30
        
        # 显示选项
        self.draw_text("显示选项", x + 10, current_y, self.colors['text'], self.font_normal)
        current_y += 25
        
        # 轨道开关
        button_rect = pygame.Rect(x + 10, current_y, 80, 25)
        self.buttons['show_orbits'] = button_rect
        self.draw_toggle_button(button_rect, "轨道", True)
        current_y += 35
        
        # 标签开关
        button_rect = pygame.Rect(x + 10, current_y, 80, 25)
        self.buttons['show_labels'] = button_rect
        self.draw_toggle_button(button_rect, "标签", True)
        current_y += 35
        
        # 网格开关
        button_rect = pygame.Rect(x + 10, current_y, 80, 25)
        self.buttons['show_grid'] = button_rect
        self.draw_toggle_button(button_rect, "网格", False)
        current_y += 35
        
    def render_info_panel(self, bodies: list, selected_body, simulation_time: float, fps: int):
        """渲染信息面板"""
        x = self.width - self.panel_width - 10
        y = 10
        width = self.panel_width
        height = 300
        
        # 面板背景
        self.draw_panel(x, y, width, height)
        
        # 标题
        self.draw_text("系统信息", x + 10, y + 10, self.colors['highlight'], self.font_large)
        
        current_y = y + 40
        
        # 天体数量
        self.draw_text(f"天体数量: {len(bodies)}", x + 10, current_y, self.colors['text'], self.font_normal)
        current_y += 25
        
        # 模拟时间
        days = simulation_time / 86400
        self.draw_text(f"模拟时间: {days:.2f} 天", x + 10, current_y, self.colors['text'], self.font_normal)
        current_y += 25
        
        # FPS
        self.draw_text(f"FPS: {fps}", x + 10, current_y, self.colors['text'], self.font_normal)
        current_y += 25
        
        # 选中天体信息
        if selected_body:
            self.draw_text(f"选中: {selected_body.name}", x + 10, current_y, self.colors['highlight'], self.font_normal)
            current_y += 25
            
            self.draw_text(f"类型: {selected_body.type}", x + 10, current_y, self.colors['text'], self.font_small)
            current_y += 20
            
            self.draw_text(f"质量: {selected_body.mass:.2e} kg", x + 10, current_y, self.colors['text'], self.font_small)
            current_y += 20
            
            position = np.linalg.norm(selected_body.position)
            self.draw_text(f"距离: {position:.0f} km", x + 10, current_y, self.colors['text'], self.font_small)
            current_y += 20
            
            velocity = np.linalg.norm(selected_body.velocity)
            self.draw_text(f"速度: {velocity:.2f} km/s", x + 10, current_y, self.colors['text'], self.font_small)
            current_y += 20
            
        # 系统能量
        if bodies:
            total_mass = sum(body.mass for body in bodies)
            self.draw_text(f"总质量: {total_mass:.2e} kg", x + 10, current_y, self.colors['text'], self.font_small)
            current_y += 20
            
    def render_status_bar(self, simulation_time: float, time_speed: float, fps: int):
        """渲染状态栏"""
        x = 0
        y = self.height - 30
        width = self.width
        height = 30
        
        # 背景
        self.draw_rect(x, y, width, height, (10, 20, 38, 200))
        
        # 状态信息
        status_text = f"状态: {'运行中' if not self.is_simulation_paused else '已暂停'} | "
        status_text += f"时间加速: {time_speed:.1f}x | "
        status_text += f"FPS: {fps}"
        
        self.draw_text(status_text, x + 10, y + 5, self.colors['text'], self.font_normal)
        
    def render_tooltips(self):
        """渲染工具提示"""
        # 这里可以添加鼠标悬停提示
        pass
        
    def draw_panel(self, x: int, y: int, width: int, height: int):
        """绘制面板背景"""
        self.draw_rect(x, y, width, height, self.colors['background'])
        self.draw_border(x, y, width, height, self.colors['border'])
        
    def draw_rect(self, x: int, y: int, width: int, height: int, color: tuple):
        """绘制矩形"""
        glColor4f(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
    def draw_border(self, x: int, y: int, width: int, height: int, color: tuple):
        """绘制边框"""
        glColor4f(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
    def draw_button(self, rect: pygame.Rect, text: str, color: tuple):
        """绘制按钮"""
        # 按钮背景
        self.draw_rect(rect.x, rect.y, rect.width, rect.height, color)
        
        # 按钮边框
        self.draw_border(rect.x, rect.y, rect.width, rect.height, self.colors['border'])
        
        # 按钮文字
        text_surface = self.font_normal.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        
        # 将Pygame表面转换为OpenGL纹理（简化处理）
        # 这里应该使用更复杂的纹理渲染，但为了简化，我们使用纯色文字
        self.draw_text(text, rect.x + rect.width//2 - len(text)*3, rect.y + 5, (0, 0, 0), self.font_normal)
        
    def draw_toggle_button(self, rect: pygame.Rect, text: str, active: bool):
        """绘制开关按钮"""
        color = self.colors['success'] if active else self.colors['warning']
        self.draw_button(rect, text, color)
        
    def draw_slider(self, rect: pygame.Rect, value: float):
        """绘制滑块"""
        # 滑块轨道
        self.draw_rect(rect.x, rect.y, rect.width, rect.height, (50, 50, 50, 200))
        
        # 滑块填充
        fill_width = int(rect.width * value)
        self.draw_rect(rect.x, rect.y, fill_width, rect.height, self.colors['highlight'])
        
        # 滑块边框
        self.draw_border(rect.x, rect.y, rect.width, rect.height, self.colors['border'])
        
    def draw_text(self, text: str, x: int, y: int, color: tuple, font):
        """绘制文字（简化版本）"""
        # 在OpenGL中绘制文字需要复杂的纹理处理
        # 这里使用简化的方法，实际应用中应该使用纹理字体
        glColor4f(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
        
        # 这里应该实现文字渲染，但为了简化，我们使用占位符
        # 实际应用中需要使用FreeType或其他字体库生成纹理
        
    def resize(self, width: int, height: int):
        """调整UI大小"""
        self.width = width
        self.height = height
        
    def toggle_simulation(self):
        """切换模拟暂停/继续"""
        self.is_simulation_paused = not self.is_simulation_paused
        
    def reset_simulation(self):
        """重置模拟"""
        # 这个应该在主程序中实现
        pass
        
    def clear_scene(self):
        """清空场景"""
        # 这个应该在主程序中实现
        pass
        
    def save_scene(self):
        """保存场景"""
        # 这个应该在主程序中实现
        pass
        
    def load_scene(self):
        """加载场景"""
        # 这个应该在主程序中实现
        pass
        
    def toggle_orbits(self):
        """切换轨道显示"""
        # 这个应该在渲染器中实现
        pass
        
    def toggle_labels(self):
        """切换标签显示"""
        # 这个应该在渲染器中实现
        pass
        
    def toggle_grid(self):
        """切换网格显示"""
        # 这个应该在渲染器中实现
        pass
        
    def set_time_speed(self, speed: float):
        """设置时间速度"""
        # 这个应该在主程序中实现
        pass