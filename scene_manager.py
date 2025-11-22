"""
场景管理器
管理和加载各种预设的天体系统场景
"""

import numpy as np
import math
from physics_engine import CelestialBody
from physics_engine import OrbitalMechanics
import random

class SceneManager:
    """场景管理器类"""
    
    def __init__(self):
        """初始化场景管理器"""
        self.G = 6.67430e-11  # 引力常数
        self.AU = 149597870.7 * 1000 # 天文单位 (km)
        
    def load_solar_system(self, bodies: list):
        """加载太阳系"""
        # 清空现有天体
        bodies.clear()
        
        # 太阳
        sun = CelestialBody(
            name='太阳',
            body_type='star',
            mass=1.989e30,
            radius=696340e3,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            color=(1.0, 0.8, 0.0)
        )
        bodies['sun'] = sun
        
        # 水星
        mercury_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 0.387 * self.AU)
        mercury = CelestialBody(
            name='水星',
            body_type='planet',
            mass=3.301e23,
            radius=2439.7e3,
            position=[0.387 * self.AU, 0, 0],
            velocity=[0, mercury_orbital_velocity, 0],
            color=(0.55, 0.47, 0.33)
        )
        bodies['mercury'] = mercury
        
        # 金星
        venus_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 0.723 * self.AU)
        venus = CelestialBody(
            name='金星',
            body_type='planet',
            mass=4.867e24,
            radius=6051.8e3,
            position=[0.723 * self.AU, 0, 0],
            velocity=[0, venus_orbital_velocity, 0],
            color=(1.0, 0.77, 0.29)
        )
        bodies['venus'] = venus
        
        # 地球
        earth_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 1.0 * self.AU)
        earth = CelestialBody(
            name='地球',
            body_type='planet',
            mass=5.972e24,
            radius=6371e3,
            position=[1.0 * self.AU, 0, 0],
            velocity=[0, earth_orbital_velocity, 0],
            color=(0.25, 0.41, 0.88)
        )
        bodies['earth'] = earth
        
        # 月球（地球的卫星）
        dist_to_earth = 384400 * 1000  # 月球距离地球的平均距离，已转换为米
        moon_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(earth.mass, dist_to_earth)
        moon = CelestialBody(
            name='月球',
            body_type='moon',
            mass=7.342e22,
            radius=1737.1e3,
            position=[1.0 * self.AU + dist_to_earth, 0, 0],
            velocity=[0, earth_orbital_velocity + moon_orbital_velocity, 0],
            color=(0.8, 0.8, 0.8)
        )
        bodies['moon'] = moon
        
        # 火星
        mars_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 1.524 * self.AU)
        mars = CelestialBody(
            name='火星',
            body_type='planet',
            mass=6.417e23,
            radius=3389.5e3,
            position=[1.524 * self.AU, 0, 0],
            velocity=[0, mars_orbital_velocity, 0],
            color=(0.8, 0.2, 0.2)
        )
        bodies['mars'] = mars
        
        # 木星
        jupiter_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 5.203 * self.AU)
        jupiter = CelestialBody(
            name='木星',
            body_type='planet',
            mass=1.898e27,
            radius=69911e3,
            position=[5.203 * self.AU, 0, 0],
            velocity=[0, jupiter_orbital_velocity, 0],
            color=(0.85, 0.65, 0.2)
        )
        bodies['jupiter'] = jupiter
        
        # 土星
        saturn_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 9.537 * self.AU)
        saturn = CelestialBody(
            name='土星',
            body_type='planet',
            mass=5.683e26,
            radius=58232e3,
            position=[9.537 * self.AU, 0, 0],
            velocity=[0, saturn_orbital_velocity, 0],
            color=(0.95, 0.82, 0.38)
        )
        bodies['saturn'] = saturn
        
        # 天王星
        uranus_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 19.191 * self.AU)
        uranus = CelestialBody(
            name='天王星',
            body_type='planet',
            mass=8.681e25,
            radius=25362e3,
            position=[19.191 * self.AU, 0, 0],
            velocity=[0, uranus_orbital_velocity, 0],
            color=(0.4, 0.8, 0.9)
        )
        bodies['uranus'] = uranus
        
        # 海王星
        neptune_orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, 30.07 * self.AU)
        neptune = CelestialBody(
            name='海王星',
            body_type='planet',
            mass=1.024e26,
            radius=24622e3,
            position=[30.07 * self.AU, 0, 0],
            velocity=[0, neptune_orbital_velocity, 0],
            color=(0.2, 0.4, 0.9)
        )
        bodies['neptune'] = neptune
        
    def load_binary_system(self, bodies: list):
        """加载双星系统"""
        bodies.clear()
        
        # 主星
        primary_star = CelestialBody(
            name='主星',
            body_type='star',
            mass=2.0e30,
            radius=696340,
            position=[-1e8, 0, 0],
            velocity=[0, 10, 0],
            color=(1.0, 0.8, 0.0)
        )
        bodies['primary'] = primary_star
        
        # 伴星
        secondary_star = CelestialBody(
            name='伴星',
            body_type='star',
            mass=1.5e30,
            radius=600000,
            position=[1e8, 0, 0],
            velocity=[0, -13.33, 0],
            color=(1.0, 0.6, 0.0)
        )
        bodies['secondary'] = secondary_star
        
        # 行星A
        planet_a_velocity = OrbitalMechanics.calculate_orbital_velocity(primary_star.mass, 2e8)
        planet_a = CelestialBody(
            name='行星A',
            body_type='planet',
            mass=6e24,
            radius=6371,
            position=[-2e8, 0, 0],
            velocity=[0, 10 + planet_a_velocity, 0],
            color=(0.2, 0.8, 0.2)
        )
        bodies['planet_a'] = planet_a
        
        # 行星B
        planet_b_velocity = OrbitalMechanics.calculate_orbital_velocity(secondary_star.mass, 2.5e8)
        planet_b = CelestialBody(
            name='行星B',
            body_type='planet',
            mass=4e24,
            radius=5000,
            position=[2.5e8, 0, 0],
            velocity=[0, -13.33 - planet_b_velocity, 0],
            color=(0.5, 0.2, 0.8)
        )
        bodies['planet_b'] = planet_b
        
    def load_random_system(self, bodies: dict):
        """加载随机系统"""
        bodies.clear()
        
        # 中央恒星
        star_mass = 1.5e30
        star = CelestialBody(
            name='恒星',
            body_type='star',
            mass=star_mass,
            radius=696340,  # 半径已转换为米
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            color=(1.0, 0.9, 0.3)
        )
        bodies['star'] = star
        
        # 随机生成行星
        import random
        colors = [(0.2, 0.4, 0.8), (0.2, 0.8, 0.2), (0.8, 0.2, 0.2), 
                 (0.8, 0.2, 0.8), (0.2, 0.8, 0.8), (0.8, 0.8, 0.2)]
        
        planet_count = random.randint(3, 6)
        
        for i in range(planet_count):
            # 随机轨道距离
            distance = (random.random() * 300 + 50) * 1e6  # 已转换为米
            angle = random.random() * 2 * math.pi
            
            # 随机质量
            mass = random.random() * 1e25 + 1e23
            radius = random.random() * 5000 + 2000  # 已转换为米
            
            # 位置
            x = math.cos(angle) * distance
            z = math.sin(angle) * distance
            y = (random.random() - 0.5) * distance * 0.1
            position = [x, y, z]
            
            # 轨道速度
            orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(star_mass, distance)
            vx = -math.sin(angle) * orbital_velocity
            vz = math.cos(angle) * orbital_velocity
            vy = (random.random() - 0.5) * 5
            velocity = [vx, vy, vz]
            
            planet = CelestialBody(
                name=f'行星{i+1}',
                body_type='planet',
                mass=mass,
                radius=radius,
                position=position,
                velocity=velocity,
                color=colors[i % len(colors)]
            )
            bodies[f'planet{i+1}'] = planet
            
    def load_triple_system(self, bodies: list):
        """加载三星系统"""
        bodies.clear()
        
        # 三颗恒星形成等边三角形配置
        distance = 1e8
        
        # 恒星1
        star1 = CelestialBody(
            name='恒星1',
            body_type='star',
            mass=1.0e30,
            radius=500000,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            color=(1.0, 1.0, 0.0)
        )
        bodies.append(star1)
        
        # 恒星2
        star2 = CelestialBody(
            name='恒星2',
            body_type='star',
            mass=0.8e30,
            radius=450000,
            position=[distance, 0, 0],
            velocity=[0, 20, 0],
            color=(1.0, 0.6, 0.0)
        )
        bodies.append(star2)
        
        # 恒星3
        star3 = CelestialBody(
            name='恒星3',
            body_type='star',
            mass=0.6e30,
            radius=400000,
            position=[distance/2, distance * math.sqrt(3)/2, 0],
            velocity=[-10 * math.sqrt(3), 10, 0],
            color=(1.0, 0.3, 0.0)
        )
        bodies.append(star3)
        
        # 添加一个围绕质心运行的行星
        planet_mass = 5e24
        planet_radius = 6000
        planet_distance = 3 * distance
        
        # 计算系统质心
        total_mass = star1.mass + star2.mass + star3.mass
        com_x = (star1.mass * star1.position[0] + star2.mass * star2.position[0] + star3.mass * star3.position[0]) / total_mass
        com_y = (star1.mass * star1.position[1] + star2.mass * star2.position[1] + star3.mass * star3.position[1]) / total_mass
        
        # 行星围绕质心运行
        planet_velocity = OrbitalMechanics.calculate_orbital_velocity(total_mass, planet_distance)
        
        planet = CelestialBody(
            name='行星',
            body_type='planet',
            mass=planet_mass,
            radius=planet_radius,
            position=[com_x + planet_distance, com_y, 0],
            velocity=[0, 0, planet_velocity],
            color=(0.2, 0.8, 0.2)
        )
        bodies.append(planet)
        
    def load_asteroid_belt(self, bodies: list):
        """加载小行星带"""
        bodies.clear()
        
        # 太阳
        sun = CelestialBody(
            name='太阳',
            body_type='star',
            mass=1.989e30,
            radius=696340,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            color=(1.0, 0.8, 0.0)
        )
        bodies.append(sun)
        
        # 木星（在小行星带外侧）
        jupiter = CelestialBody(
            name='木星',
            body_type='planet',
            mass=1.898e27,
            radius=69911,
            position=[5.203 * self.AU, 0, 0],
            velocity=[0, OrbitalMechanics.calculate_orbital_velocity(sun.mass, 5.203 * self.AU), 0],
            color=(0.85, 0.65, 0.2)
        )
        bodies.append(jupiter)
        
        # 生成小行星
        num_asteroids = 50
        for i in range(num_asteroids):
            # 小行星带范围 (2.0 - 3.5 AU)
            distance = (2.0 + random.random() * 1.5) * self.AU
            angle = random.random() * 2 * math.pi
            
            # 小行星参数
            mass = random.random() * 1e20 + 1e15
            radius = random.random() * 100 + 10
            
            # 位置
            x = math.cos(angle) * distance
            z = math.sin(angle) * distance
            y = (random.random() - 0.5) * distance * 0.05
            position = [x, y, z]
            
            # 速度（考虑木星扰动）
            base_velocity = OrbitalMechanics.calculate_orbital_velocity(sun.mass, distance)
            velocity_perturbation = (random.random() - 0.5) * 2
            
            vx = -math.sin(angle) * (base_velocity + velocity_perturbation)
            vz = math.cos(angle) * (base_velocity + velocity_perturbation)
            vy = (random.random() - 0.5) * 1
            velocity = [vx, vy, vz]
            
            asteroid = CelestialBody(
                name=f'小行星{i+1}',
                body_type='asteroid',
                mass=mass,
                radius=radius,
                position=position,
                velocity=velocity,
                color=(0.55, 0.45, 0.33)
            )
            bodies.append(asteroid)
            
    def load_black_hole_system(self, bodies: list):
        """加载黑洞系统"""
        bodies.clear()
        
        # 超大质量黑洞 (类似银河系中心黑洞)
        black_hole_mass = 4e6 * 1.989e30  # 4百万太阳质量
        schwarzschild_radius = 2 * self.G * black_hole_mass / (299792.458**2)  # 史瓦西半径
        
        black_hole = CelestialBody(
            name='黑洞',
            body_type='star',  # 使用star类型以便渲染
            mass=black_hole_mass,
            radius=schwarzschild_radius,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            color=(0.0, 0.0, 0.0)
        )
        bodies.append(black_hole)
        
        # 围绕黑洞运行的恒星
        num_stars = 10
        for i in range(num_stars):
            # 随机轨道参数（接近黑洞）
            distance = (5 + i * 2) * schwarzschild_radius
            angle = i * 2 * math.pi / num_stars
            
            # 计算相对论修正的轨道速度
            classical_velocity = OrbitalMechanics.calculate_orbital_velocity(black_hole_mass, distance)
            # 添加相对论修正
            relativistic_factor = 1 + 3 * schwarzschild_radius / distance
            orbital_velocity = classical_velocity * math.sqrt(relativistic_factor)
            
            # 位置
            x = math.cos(angle) * distance
            z = math.sin(angle) * distance
            y = (i % 2) * distance * 0.1  # 轻微倾斜
            position = [x, y, z]
            
            # 速度
            vx = -math.sin(angle) * orbital_velocity
            vz = math.cos(angle) * orbital_velocity
            vy = 0
            velocity = [vx, vy, vz]
            
            # 恒星颜色根据距离变化
            color_intensity = 1.0 - i / num_stars * 0.5
            star = CelestialBody(
                name=f'恒星{i+1}',
                body_type='star',
                mass=1.989e30,
                radius=696340,
                position=position,
                velocity=velocity,
                color=(color_intensity, color_intensity * 0.8, color_intensity * 0.3)
            )
            bodies.append(star)
            
    def save_scene(self, bodies: list, filename: str):
        """保存场景到文件"""
        import json
        
        scene_data = {
            'timestamp': '2023-12-01T12:00:00',
            'bodies': []
        }
        
        for body in bodies:
            body_data = {
                'name': body.name,
                'type': body.type,
                'mass': body.mass,
                'radius': body.radius,
                'position': body.position.tolist(),
                'velocity': body.velocity.tolist(),
                'color': list(body.color)
            }
            scene_data['bodies'].append(body_data)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, indent=2, ensure_ascii=False)
            
    def load_scene(self, bodies: list, filename: str):
        """从文件加载场景"""
        import json
        
        with open(filename, 'r', encoding='utf-8') as f:
            scene_data = json.load(f)
            
        bodies.clear()
        
        for body_data in scene_data['bodies']:
            body = CelestialBody(
                name=body_data['name'],
                type=body_data['type'],
                mass=body_data['mass'],
                radius=body_data['radius'],
                position=body_data['position'],
                velocity=body_data['velocity'],
                color=tuple(body_data['color'])
            )
            bodies.append(body)