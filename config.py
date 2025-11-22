"""
配置文件
包含所有全局配置和常量定义
"""

# 窗口配置
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_TITLE = "天体系统模拟器"

# 物理配置
GRAVITATIONAL_CONSTANT = 6.67430e-11  # 引力常数 (N·m²/kg²)
SPEED_OF_LIGHT = 299792458  # 光速 (m/s)

# 天文常数
ASTRONOMICAL_UNIT = 149597870700  # 天文单位 (m)
SOLAR_MASS = 1.989e30  # 太阳质量 (kg)
SOLAR_RADIUS = 696340000  # 太阳半径 (m)

# 模拟配置
DEFAULT_TIME_STEP = 3600  # 默认时间步长 (秒)
MAX_TIME_SPEED = 1000.0  # 最大时间加速倍数
MIN_TIME_SPEED = 0.1  # 最小时间加速倍数

# 渲染配置
BACKGROUND_COLOR = (0.02, 0.02, 0.05)  # 背景色 (深空蓝)
STAR_COUNT = 5000  # 星空中的恒星数量
MAX_TRAIL_LENGTH = 1000  # 轨迹最大长度

# 渲染缩放：将物理单位（米）转换为渲染单位（OpenGL 单位）
# 例如 RENDER_SCALE = 1e-9 将把 1 米 映射为 1e-9 渲染单位，
# 使天体坐标（米级）能在可视范围内显示。
RENDER_SCALE = 2e-11
# 天体类型和颜色
BODY_TYPES = {
    'star': {
        'name': '恒星',
        'default_mass': 1.989e30,
        'default_radius': 696340,
        'color': (1.0, 0.8, 0.0),
        'emissive': True
    },
    'planet': {
        'name': '行星',
        'default_mass': 5.972e24,
        'default_radius': 6371,
        'color': (0.25, 0.41, 0.88),
        'emissive': False
    },
    'moon': {
        'name': '卫星',
        'default_mass': 7.342e22,
        'default_radius': 1737,
        'color': (0.8, 0.8, 0.8),
        'emissive': False
    },
    'asteroid': {
        'name': '小行星',
        'default_mass': 1e15,
        'default_radius': 100,
        'color': (0.55, 0.45, 0.33),
        'emissive': False
    }
}

# 预设场景配置
PRESET_SCENES = {
    'solar_system': {
        'name': '太阳系',
        'description': '我们熟悉的太阳系模型',
        'difficulty': 'simple',
        'bodies_count': 9
    },
    'binary_system': {
        'name': '双星系统',
        'description': '两颗恒星相互围绕的系统',
        'difficulty': 'medium',
        'bodies_count': 4
    },
    'triple_system': {
        'name': '三星系统',
        'description': '经典的三体问题',
        'difficulty': 'hard',
        'bodies_count': 4
    },
    'asteroid_belt': {
        'name': '小行星带',
        'description': '大量小天体组成的系统',
        'difficulty': 'medium',
        'bodies_count': 50
    },
    'black_hole': {
        'name': '黑洞系统',
        'description': '超大质量黑洞周围的恒星',
        'difficulty': 'extreme',
        'bodies_count': 10
    }
}

# 相机配置
# 使用更大的默认相机距离（米），适用于观测太阳系级别的场景
DEFAULT_CAMERA_DISTANCE = 3.0e11
DEFAULT_CAMERA_ROTATION = [0.0, 0.0]  # [pitch, yaw]
CAMERA_SENSITIVITY = 0.5
ZOOM_SENSITIVITY = 0.1

# 物理计算配置
USE_RK4_INTEGRATION = True  # 是否使用RK4积分方法
ENABLE_COLLISION_DETECTION = True  # 是否启用碰撞检测
ENABLE_RELATIVISTIC_CORRECTIONS = False  # 是否启用相对论修正

# 性能配置
TARGET_FPS = 60
MAX_PHYSICS_STEPS_PER_FRAME = 10
ENABLE_MULTITHREADING = False  # 是否启用多线程
USE_CUDA = False  # 是否使用CUDA加速

# 数据保存配置
AUTO_SAVE_INTERVAL = 300  # 自动保存间隔（秒）
SCENE_FILE_EXTENSION = '.json'
SCREENSHOT_FORMAT = 'PNG'

# 用户界面配置
UI_PANEL_WIDTH = 250
UI_FONT_SIZE_SMALL = 12
UI_FONT_SIZE_NORMAL = 14
UI_FONT_SIZE_LARGE = 18

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'celestial_simulator.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 调试配置
DEBUG_MODE = False
SHOW_PHYSICS_DEBUG_INFO = False
SHOW_PERFORMANCE_STATS = True
ENABLE_PROFILING = False

# 天体物理常数
EARTH_MASS = 5.972e24  # 地球质量 (kg)
EARTH_RADIUS = 6371000  # 地球半径 (m)
MOON_MASS = 7.342e22  # 月球质量 (kg)
MOON_RADIUS = 1737100  # 月球半径 (m)

# 轨道参数
import math
ESCAPE_VELOCITY_FACTOR = math.sqrt(2)  # 逃逸速度因子
CIRCULAR_ORBIT_ECCENTRICITY = 0.0  # 圆轨道偏心率
PARABOLIC_ORBIT_ENERGY = 0.0  # 抛物线轨道能量

# 数值精度配置
POSITION_TOLERANCE = 1e-10  # 位置计算容差
VELOCITY_TOLERANCE = 1e-10  # 速度计算容差
FORCE_TOLERANCE = 1e-15  # 力计算容差

# 文件路径配置
ASSETS_DIR = 'assets'
TEXTURES_DIR = f'{ASSETS_DIR}/textures'
FONTS_DIR = f'{ASSETS_DIR}/fonts'
SCENES_DIR = 'scenes'
SCREENSHOTS_DIR = 'screenshots'

# 版本信息
VERSION = '1.0.0'
AUTHOR = '天体系统模拟器开发团队'
COPYRIGHT = '© 2023 天体系统模拟器'