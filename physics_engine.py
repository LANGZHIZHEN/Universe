"""
天体物理引擎
包含引力计算、天体类和物理模拟核心功能
"""

import numpy as np
import math
from typing import List, Tuple, Dict

class CelestialBody:
    """天体类 - 表示宇宙中的各种天体"""
    
    def __init__(self, name: str, body_type: str, mass: float, radius: float, 
                 position: List[float], velocity: List[float], color: Tuple[float, float, float]):
        """
        初始化天体
        
        Args:
            name: 天体名称
            body_type: 天体类型 ('star', 'planet', 'moon', 'asteroid')
            mass: 质量 (kg)
            radius: 半径 (km)
            position: 位置坐标 [x, y, z] (km)
            velocity: 速度向量 [vx, vy, vz] (km/s)
            color: RGB颜色 (0-1范围)
        """
        self.name = name
        self.type = body_type
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.color = color
        
        # 轨道相关
        self.trail = []  # 轨道轨迹点
        self.max_trail_length = 1000
        self.orbit_calculated = False
        self.semi_major_axis = 0.0
        self.eccentricity = 0.0
        self.period = 0.0
        
        # 渲染相关
        self.display_list = None
        self.label_texture = None
        
        # 物理属性
        self.force = np.zeros(3, dtype=np.float64)
        self.acceleration = np.zeros(3, dtype=np.float64)
        
    def update_position(self, dt: float):
        """更新天体位置"""
        # 使用RK4积分方法更新位置和速度
        self.position += self.velocity * dt
        
        # 更新轨迹
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
    def update_velocity(self, dt: float):
        """更新天体速度"""
        self.velocity += self.acceleration * dt
        
    def get_kinetic_energy(self) -> float:
        """计算动能"""
        speed = np.linalg.norm(self.velocity)
        return 0.5 * self.mass * speed * speed
        
    def get_potential_energy(self, other_bodies: List['CelestialBody']) -> float:
        """计算引力势能"""
        G = 6.67430e-11  # 引力常数
        potential_energy = 0.0
        
        for other in other_bodies:
            if other is not self:
                distance = np.linalg.norm(self.position - other.position)
                if distance > 0:
                    potential_energy -= G * self.mass * other.mass / distance
                    
        return potential_energy
        
    def calculate_orbit_parameters(self, central_body: 'CelestialBody'):
        """计算轨道参数（相对于中心天体）"""
        if central_body is None or central_body is self:
            return
            
        # 相对位置和速度
        r_vec = self.position - central_body.position
        v_vec = self.velocity - central_body.velocity
        
        r = np.linalg.norm(r_vec)
        v = np.linalg.norm(v_vec)
        
        if r == 0 or v == 0:
            return
            
        G = 6.67430e-11
        mu = G * (self.mass + central_body.mass)
        
        # 比角动量
        h_vec = np.cross(r_vec, v_vec)
        h = np.linalg.norm(h_vec)
        
        if h == 0:
            return
            
        # 轨道能量
        energy = 0.5 * v * v - mu / r
        
        # 半长轴
        if abs(energy) > 1e-10:
            self.semi_major_axis = -mu / (2 * energy)
        else:
            self.semi_major_axis = float('inf')
            
        # 偏心率
        e_vec = np.cross(v_vec, h_vec) / mu - r_vec / r
        self.eccentricity = np.linalg.norm(e_vec)
        
        # 轨道周期（开普勒第三定律）
        if self.semi_major_axis > 0 and self.semi_major_axis != float('inf'):
            self.period = 2 * math.pi * math.sqrt(self.semi_major_axis**3 / mu)
        else:
            self.period = float('inf')
            
        self.orbit_calculated = True
        
    def is_collision_with(self, other: 'CelestialBody') -> bool:
        """检测与另一天体的碰撞"""
        distance = np.linalg.norm(self.position - other.position)
        return distance < (self.radius + other.radius)
        
    def merge_with(self, other: 'CelestialBody'):
        """与另一天体合并（碰撞后）"""
        # 动量守恒
        total_mass = self.mass + other.mass
        self.velocity = (self.mass * self.velocity + other.mass * other.velocity) / total_mass
        
        # 更新质量和半径（假设密度不变）
        self.mass = total_mass
        # 体积相加，重新计算半径
        total_volume = (4/3) * math.pi * (self.radius**3 + other.radius**3)
        self.radius = (total_volume * 3 / (4 * math.pi))**(1/3)
        
        # 位置调整到质心
        self.position = (self.mass * self.position + other.mass * other.position) / total_mass
        
    def __str__(self):
        return f"{self.name} ({self.type}) - 质量: {self.mass:.2e}kg, 位置: {self.position}, 速度: {self.velocity}m/s, 半径: {self.radius}m"
        
    def __repr__(self):
        return self.__str__()

class GravityEngine:
    """引力引擎 - 处理天体间的引力相互作用"""
    
    def __init__(self):
        self.G = 6.67430e-11  # 引力常数
        self.use_rk4 = True  # 使用RK4积分方法
        
    def calculate_gravitational_forces(self, bodies: List[CelestialBody]) -> List[np.ndarray]:
        """
        计算所有天体间的引力
        
        Returns:
            每个天体受到的合力列表
        """
        forces = {body: np.zeros(3) for body in bodies}
        
        body_list = list(bodies.values())  # 获取天体对象列表
        body_keys = list(bodies.keys())  # 获取天体键（如 'earth', 'sun' 等）
        
        for i in range(len(body_list)):
            for j in range(i + 1, len(body_list)):
                body1, body2 = body_list[i], body_list[j]
                
                # 计算距离向量
                r_vec = body2.position - body1.position
                r = np.linalg.norm(r_vec)
                
                if r == 0:
                    continue  # 如果两个天体位置相同，则跳过（避免除零错误）
                    
                # 计算引力大小
                force_magnitude = self.G * body1.mass * body2.mass / (r * r)
                
                # 计算引力方向
                force_direction = r_vec / r
                
                # 应用引力（作用力与反作用力）
                forces[body_keys[i]] += force_direction * force_magnitude
                forces[body_keys[j]] -= force_direction * force_magnitude  # 反作用力
        
        return forces
        
    def update_accelerations(self, bodies: dict, forces: dict):
        """更新天体的加速度"""
        for body_key, body in bodies.items():
            if body.mass > 0:
                body.acceleration = forces[body_key] / body.mass
                
    def euler_integration(self, bodies: dict, dt: float):
        """欧拉积分方法"""
        # 计算力
        forces = self.calculate_gravitational_forces(bodies)
        
        # 更新加速度
        self.update_accelerations(bodies, forces)
        
        # 更新速度和位置
        for body in bodies.values():
            body.update_velocity(dt)
            body.update_position(dt)
            
    def rk4_integration(self, bodies: dict, dt: float):
        """Runge-Kutta 4阶积分方法"""
        # 保存初始状态
        initial_positions = {body_key: body.position.copy() for body_key, body in bodies.items()}
        initial_velocities = {body_key: body.velocity.copy() for body_key, body in bodies.items()}
        
        # RK4积分步骤
        k1_pos, k1_vel = self._rk4_step(bodies, dt, 0)
        
        # 应用k1
        for body_key, body in bodies.items():
            body.position = initial_positions[body_key] + 0.5 * k1_pos[body_key] * dt
            body.velocity = initial_velocities[body_key] + 0.5 * k1_vel[body_key] * dt
            
        k2_pos, k2_vel = self._rk4_step(bodies, dt, 0.5 * dt)
        
        # 应用k2
        for body_key, body in bodies.items():
            body.position = initial_positions[body_key] + 0.5 * k2_pos[body_key] * dt
            body.velocity = initial_velocities[body_key] + 0.5 * k2_vel[body_key] * dt
            
        k3_pos, k3_vel = self._rk4_step(bodies, dt, 0.5 * dt)
        
        # 应用k3
        for body_key, body in bodies.items():
            body.position = initial_positions[body_key] + k3_pos[body_key] * dt
            body.velocity = initial_velocities[body_key] + k3_vel[body_key] * dt
            
        k4_pos, k4_vel = self._rk4_step(bodies, dt, dt)
        
        # 最终更新
        for body_key, body in bodies.items():
            body.position = initial_positions[body_key] + (k1_pos[body_key] + 2*k2_pos[body_key] + 2*k3_pos[body_key] + k4_pos[body_key]) * dt / 6
            body.velocity = initial_velocities[body_key] + (k1_vel[body_key] + 2*k2_vel[body_key] + 2*k3_vel[body_key] + k4_vel[body_key]) * dt / 6

    def _rk4_step(self, bodies: dict, dt: float, t: float) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """RK4积分的一个步骤"""
        # 计算当前状态的力
        forces = self.calculate_gravitational_forces(bodies)
        
        positions = {}
        velocities = {}
        
        for body_key, body in bodies.items():
            # 位置变化率 = 当前速度
            positions[body_key] = body.velocity.copy()
            
            # 速度变化率 = 当前加速度
            if body.mass > 0:
                acceleration = forces[body_key] / body.mass
            else:
                acceleration = np.zeros(3)
            velocities[body_key] = acceleration
            
        return positions, velocities
        
    def update_positions(self, bodies: dict, dt: float):
        """更新所有天体的位置"""
        if self.use_rk4:
            self.rk4_integration(bodies, dt)
        else:
            self.euler_integration(bodies, dt)
            
        # 处理碰撞
        self.handle_collisions(bodies)
        
    def handle_collisions(self, bodies: dict):
        """处理天体间的碰撞"""
        for i, body_key_1 in enumerate(bodies):
            for j, body_key_2 in enumerate(bodies):
                if i >= j:
                    continue  # 跳过重复的对
                if bodies[body_key_1].is_collision_with(bodies[body_key_2]):
                    # 合并两个天体
                    bodies[body_key_1].merge_with(bodies[body_key_2])
                    # 移除被合并的天体
                    del bodies[body_key_2]
                    break
                    
    def calculate_system_energy(self, bodies: dict) -> float:
        """计算系统的总能量"""
        total_kinetic = 0.0
        total_potential = 0.0
        
        # 计算总动能
        for body in bodies.values():
            total_kinetic += body.get_kinetic_energy()
            
        # 计算总势能
        for body_key_1, body_1 in bodies.items():
            for body_key_2, body_2 in bodies.items():
                if body_key_1 >= body_key_2:
                    continue  # 跳过重复的对
                distance = np.linalg.norm(body_1.position - body_2.position)
                if distance > 0:
                    total_potential -= self.G * body_1.mass * body_2.mass / distance
        return total_kinetic + total_potential
    
    def calculate_angular_momentum(self, bodies: dict) -> np.ndarray:
        """计算系统的总角动量"""
        total_angular_momentum = np.zeros(3, dtype=np.float64)
        
        for body in bodies.values():
            angular_momentum = np.cross(body.position, body.mass * body.velocity)
            total_angular_momentum += angular_momentum
            
        return total_angular_momentum
        
    def find_center_of_mass(self, bodies: dict) -> np.ndarray:
        """计算系统的质心"""
        total_mass = sum(body.mass for body in bodies.values())
        if total_mass == 0:
            return np.zeros(3)
            
        center_of_mass = np.zeros(3, dtype=np.float64)
        for body in bodies.values():
            center_of_mass += body.mass * body.position
            
        return center_of_mass / total_mass
        
    def find_center_of_mass_velocity(self, bodies: dict) -> np.ndarray:
        """计算系统的质心速度"""
        total_mass = sum(body.mass for body in bodies.values())
        if total_mass == 0:
            return np.zeros(3)
            
        center_of_mass_velocity = np.zeros(3, dtype=np.float64)
        for body in bodies.values():
            center_of_mass_velocity += body.mass * body.velocity
            
        return center_of_mass_velocity / total_mass
        
    def apply_correction(self, bodies: dict):
        """应用数值修正（能量和角动量守恒）"""
        # 将系统质心移到原点
        com = self.find_center_of_mass(bodies)
        for body in bodies.values():
            body.position -= com
            
        # 将系统质心速度设为零
        com_velocity = self.find_center_of_mass_velocity(bodies)
        for body in bodies.values():
            body.velocity -= com_velocity
            
class OrbitalMechanics:
    """轨道力学工具类"""
    
    @staticmethod
    def calculate_orbital_velocity(central_mass: float, orbital_radius: float) -> float:
        """计算圆形轨道速度"""
        G = 6.67430e-11
        return math.sqrt(G * central_mass / orbital_radius)
        
    @staticmethod
    def calculate_escape_velocity(central_mass: float, distance: float) -> float:
        """计算逃逸速度"""
        G = 6.67430e-11
        return math.sqrt(2 * G * central_mass / distance)
        
    @staticmethod
    def calculate_orbital_period(central_mass: float, semi_major_axis: float) -> float:
        """计算轨道周期（开普勒第三定律）"""
        G = 6.67430e-11
        return 2 * math.pi * math.sqrt(semi_major_axis**3 / (G * central_mass))
        
    @staticmethod
    def calculate_hohmann_transfer_delta_v(central_mass: float, r1: float, r2: float) -> Tuple[float, float]:
        """计算霍曼转移所需的速度变化"""
        G = 6.67430e-11
        
        # 初始轨道速度
        v1 = math.sqrt(G * central_mass / r1)
        
        # 最终轨道速度
        v2 = math.sqrt(G * central_mass / r2)
        
        # 转移轨道半长轴
        a_transfer = (r1 + r2) / 2
        
        # 转移轨道在近地点和远地点的速度
        v_transfer_periapsis = math.sqrt(G * central_mass * (2/r1 - 1/a_transfer))
        v_transfer_apoapsis = math.sqrt(G * central_mass * (2/r2 - 1/a_transfer))
        
        # 两次速度变化
        delta_v1 = v_transfer_periapsis - v1
        delta_v2 = v2 - v_transfer_apoapsis
        
        return delta_v1, delta_v2