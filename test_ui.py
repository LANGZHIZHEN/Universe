import unittest
import pygame
from unittest.mock import MagicMock
from ui_manager import UIManager
from celestial_simulator import CelestialBody  # 假设你有天体类
from physics_engine import OrbitalMechanics  # 如果涉及物理引擎
from renderer import OpenGLRenderer  # 如果涉及渲染器

class TestUIManager(unittest.TestCase):
    
    def setUp(self):
        """在每个测试前初始化pygame和UIManager"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.ui_manager = UIManager(800, 600)  # 创建UIManager对象
        self.ui_manager.font = pygame.font.SysFont("Arial", 20)  # 设置字体
        self.renderer = OpenGLRenderer(self.ui_manager.width, self.ui_manager.height)  # 创建渲染器实例

        # 创建一些虚拟的天体，用于测试UI显示
        self.sun = CelestialBody(name='Sun', body_type='star', mass=1.989e30, radius=696340, position=[0, 0, 0], velocity=[0, 0, 0], color=(1.0, 1.0, 0.0))
        self.earth = CelestialBody(name='Earth', body_type='planet', mass=5.972e24, radius=6371e3, position=[1.0 * 149597870.7 * 1000, 0, 0], velocity=[0, 29780, 0], color=(0.25, 0.41, 0.88))
        
        self.bodies = {'sun': self.sun, 'earth': self.earth}

    def tearDown(self):
        """在每个测试后退出pygame"""
        pygame.quit()

    def test_initialization(self):
        """测试UIManager是否正确初始化"""
        self.assertIsInstance(self.ui_manager, UIManager)
        self.assertEqual(self.ui_manager.width, 800)
        self.assertEqual(self.ui_manager.height, 600)
        self.assertEqual(self.ui_manager.buttons, {})

    def test_render_control_panel(self):
        """测试渲染控制面板"""
        self.ui_manager.render_control_panel(1.0, 60)  # 假设时间速率为1.0，帧率为60
        # 检查是否渲染了“暂停”按钮
        button = self.ui_manager.buttons.get('play_pause')
        self.assertIsNotNone(button)  # 按钮应该已经渲染
        self.assertEqual(button.width, 100)
        self.assertEqual(button.height, 30)
        
    def test_toggle_simulation_pause(self):
        """测试暂停和继续的按钮功能"""
        self.ui_manager.is_simulation_paused = False  # 初始状态是模拟正在运行
        self.ui_manager.toggle_simulation()  # 点击暂停按钮
        self.assertTrue(self.ui_manager.is_simulation_paused)  # 模拟应该暂停
        
        self.ui_manager.toggle_simulation()  # 点击继续按钮
        self.assertFalse(self.ui_manager.is_simulation_paused)  # 模拟应该继续运行
        
    def test_pick_body(self):
        """测试鼠标点击天体（选择天体）"""
        # 模拟鼠标点击事件
        mouse_pos = (400, 300)  # 假设鼠标点击了屏幕中心
        selected_body = self.renderer.pick_body(mouse_pos, self.bodies, 500.0, [0, 0])
        
        # 我们期望选择的是地球
        self.assertEqual(selected_body, self.earth)

    def test_render_highlight_selected_body(self):
        """测试选中天体时是否正确高亮显示"""
        # 渲染地球时，应该正确高亮显示
        self.ui_manager.selected_body = self.earth
        self.renderer.render_celestial_bodies(self.bodies, self.earth)
        
        # 检查渲染过程中是否发生了正确的高亮操作（这需要依赖OpenGL的渲染结果，实际测试时需结合渲染输出）
        # 这里假设有相关的渲染逻辑来检测高亮效果
        # 比如检查glColor等渲染状态的变化
        
    def test_update_ui(self):
        """测试模拟状态更改时，UI是否正确更新"""
        # 初始状态下，按钮显示暂停
        self.ui_manager.is_simulation_paused = False
        self.ui_manager.render_control_panel(1.0, 60)  # 假设时间速率为1.0，帧率为60
        button = self.ui_manager.buttons.get('play_pause')
        # 检查按钮的文本是否为“暂停”
        self.assertEqual(button.text, "暂停")
        
        # 模拟点击按钮，暂停模拟
        self.ui_manager.toggle_simulation()
        self.ui_manager.render_control_panel(1.0, 60)
        button = self.ui_manager.buttons.get('play_pause')
        # 检查按钮的文本是否为“继续”
        self.assertEqual(button.text, "继续")
        

if __name__ == '__main__':
    unittest.main()
