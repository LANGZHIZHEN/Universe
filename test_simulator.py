#!/usr/bin/env python3
"""
天体系统模拟器测试脚本
用于验证各个模块的功能是否正常
"""

import sys
import numpy as np
import time
from physics_engine import CelestialBody, GravityEngine, OrbitalMechanics
from scene_manager import SceneManager
import math

def test_celestial_body():
    """测试天体类"""
    print("正在测试天体类...")
    
    # 创建地球
    earth = CelestialBody(
        name='地球',
        body_type='planet',
        mass=5.972e24,
        radius=6371,
        position=[149597870.7, 0, 0],  # 1 AU
        velocity=[0, 29.78, 0],  # 轨道速度
        color=(0.25, 0.41, 0.88)
    )
    
    # 测试基本属性
    assert earth.name == '地球'
    assert earth.type == 'planet'
    assert abs(earth.mass - 5.972e24) < 1e20
    assert abs(earth.radius - 6371) < 1
    
    # 测试位置和速度
    assert abs(earth.position[0] - 149597870.7) < 1e6
    assert abs(earth.velocity[1] - 29.78) < 0.1
    
    # 测试动能计算
    kinetic_energy = earth.get_kinetic_energy()
    expected_ke = 0.5 * earth.mass * (29.78**2)
    assert abs(kinetic_energy - expected_ke) / expected_ke < 0.01
    
    print("√ 天体类测试通过")
    return earth

def test_gravity_engine():
    """测试引力引擎"""
    print("正在测试引力引擎...")
    
    # 创建太阳和地球
    sun = CelestialBody(
        name='太阳',
        body_type='star',
        mass=1.989e30,
        radius=696340,
        position=[0, 0, 0],
        velocity=[0, 0, 0],
        color=(1.0, 0.8, 0.0)
    )
    
    earth = CelestialBody(
        name='地球',
        body_type='planet',
        mass=5.972e24,
        radius=6371,
        position=[149597870.7, 0, 0],
        velocity=[0, 29.78, 0],
        color=(0.25, 0.41, 0.88)
    )
    
    bodies = {
        'sun': sun,
        'earth': earth
    }
    
    # 创建引力引擎
    engine = GravityEngine()
    
    # 测试引力计算
    forces = engine.calculate_gravitational_forces(bodies)
    
    # 计算预期的引力
    G = 6.67430e-11
    distance = 149597870.7
    expected_force = G * sun.mass * earth.mass / (distance**2)
    
    # 地球受到的力应该指向太阳（负方向）
    earth_force = forces['earth']
    assert earth_force[0] < 0  # x方向为负
    assert abs(earth_force[0]) > abs(earth_force[1])  # x方向力最大
    
    # 测试系统能量计算
    total_energy = engine.calculate_system_energy(bodies)
    assert total_energy < 0  # 束缚系统能量为负
    
    print("√ 引力引擎测试通过")
    return engine, bodies

def test_orbital_mechanics():
    """测试轨道力学"""
    print("正在测试轨道力学...")
    
    # 测试圆轨道速度
    sun_mass = 1.989e30
    earth_distance = 149597870.7 * 1000  # 转换为米
    
    orbital_velocity = OrbitalMechanics.calculate_orbital_velocity(sun_mass, earth_distance)
    expected_velocity = 29780  # km/s
    assert abs(orbital_velocity - expected_velocity) / expected_velocity < 0.01
    
    # 测试逃逸速度
    escape_velocity = OrbitalMechanics.calculate_escape_velocity(sun_mass, earth_distance)
    expected_escape = expected_velocity * math.sqrt(2)
    
    assert abs(escape_velocity - expected_escape) / expected_escape < 0.01
    
    # 测试轨道周期
    orbital_period = OrbitalMechanics.calculate_orbital_period(sun_mass, earth_distance)
    expected_period = 365.25 * 24 * 3600  # 一年
    
    assert abs(orbital_period - expected_period) / expected_period < 0.01
    
    print("√ 轨道力学测试通过")

def test_scene_manager():
    """测试场景管理器"""
    print("正在测试场景管理器...")
    
    manager = SceneManager()
    bodies = dict()
    
    # 测试加载太阳系
    manager.load_solar_system(bodies)
    assert len(bodies) == 10  # 太阳 + 8颗行星
    assert bodies['sun'].name == '太阳'
    assert bodies['mercury'].name == '水星'
    
    # 验证轨道速度
    earth = bodies['earth']  # 地球是第5个天体（太阳+水星+金星+地球）
    expected_orbital_velocity = 29780  # m/s
    assert abs(earth.velocity[1] - expected_orbital_velocity) / expected_orbital_velocity < 0.01
    
    # 测试加载双星系统
    bodies.clear()
    manager.load_binary_system(bodies)
    assert len(bodies) == 4  # 2颗恒星 + 2颗行星
    assert bodies['primary'].name == '主星'
    assert bodies['secondary'].name == '伴星'
    
    print("√ 场景管理器测试通过")
    return manager

def test_physics_simulation():
    """测试物理模拟"""
    print("正在测试物理模拟...")
    
    # 创建简单的双体系统
    sun = CelestialBody(
        name='太阳',
        body_type='star',
        mass=1.989e30,
        radius=696340e3,
        position=[0, 0, 0],
        velocity=[0, 0, 0],
        color=(1.0, 0.8, 0.0)
    )
    
    earth = CelestialBody(
        name='地球',
        body_type='planet',
        mass=5.972e24,
        radius=6371e3,
        position=[149597870.7e3, 0, 0],
        velocity=[0, 29780, 0],
        color=(0.25, 0.41, 0.88)
    )
    
    bodies = {
        'sun': sun,
        'earth': earth
    }
    engine = GravityEngine()
    # 运行短时间模拟
    dt = 3600  # 1小时
    initial_energy = engine.calculate_system_energy(bodies)
    for step in range(100):
        engine.update_positions(bodies, dt)
    final_energy = engine.calculate_system_energy(bodies)
    # 能量应该基本守恒（数值误差范围内）
    energy_change = abs(final_energy - initial_energy) / abs(initial_energy)
    assert energy_change < 0.01  # 能量变化小于1%
    
    # 地球应该大致回到初始位置（完成一个周期的1/24）
    earth_final_pos = earth.position
    expected_angle = 2 * math.pi * 100 / (365.25 * 24)  # 100小时的角度
    expected_x = 149597870.7e3 * math.cos(expected_angle)
    expected_y = 149597870.7e3 * math.sin(expected_angle)
    
    distance_error = np.linalg.norm(earth_final_pos - [expected_x, expected_y, 0])
    assert distance_error < 1e7  # 位置误差小于1000km
    
    print("√ 物理模拟测试通过")

def test_performance():
    """测试性能"""
    print("正在测试性能...")
    
    # 创建包含多个天体的系统
    bodies = dict()
    
    # 中心恒星
    sun = CelestialBody(
        name='太阳',
        body_type='star',
        mass=1.989e30,
        radius=69634e3,
        position=[0, 0, 0],
        velocity=[0, 0, 0],
        color=(1.0, 0.8, 0.0)
    )
    bodies['sun'] = sun
    
    # 添加多个行星
    for i in range(8):
        angle = i * math.pi / 4
        distance = (i + 1) * 1e8
        velocity = math.sqrt(6.67430e-11 * sun.mass / distance)
        
        planet = CelestialBody(
            name=f'行星{i+1}',
            body_type='planet',
            mass=5.972e24,
            radius=6371e3,
            position=[distance * math.cos(angle), 0, distance * math.sin(angle)],
            velocity=[-velocity * math.sin(angle), 0, velocity * math.cos(angle)],
            color=(0.25, 0.41, 0.88)
        )
        bodies[f"planet_{i}"] = planet
    
    engine = GravityEngine()
    
    # 测试计算性能
    start_time = time.time()
    for _ in range(100):
        engine.calculate_gravitational_forces(bodies)
    end_time = time.time()
    
    calculation_time = end_time - start_time
    print(f"100次引力计算耗时: {calculation_time:.3f}秒")
    
    assert calculation_time < 1.0  # 应该在1秒内完成
    
    print("√ 性能测试通过")

def main():
    """主测试函数"""
    print("开始天体系统模拟器测试...")
    print("=" * 50)
    
    try:
        # 运行所有测试
        test_celestial_body()
        test_gravity_engine()
        test_orbital_mechanics()
        test_scene_manager()
        test_physics_simulation()
        test_performance()
        
        print("=" * 50)
        print("＜（＾－＾）＞ 所有测试通过！")
        print("天体系统模拟器功能正常，可以运行主程序。")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)