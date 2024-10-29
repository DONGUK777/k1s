import subprocess
import json
import time

# 기본 설정값
cpu_scale_out = 50.0  
cpu_scale_in = 30.0   
# check_interval = 1    
target_container_name = 'samdul-load_balancer-1'  

def get_docker_stats(container_name):
    try:
        r = subprocess.check_output(
            ["docker", "stats", "samdul-load_balancer-1", "--no-stream", "--format", "{{json .}}"],
            text=True
        )
        return json.loads(r)
    except subprocess.CalledProcessError as e:
        print(f"Error while getting stats for {container_name}: {e}")
        return None

def scale_out(current_scale):
    new_scale = current_scale + 1  # 현재 스케일에서 1 증가
    print() 
    print("Scale out...")
    print(f"Scale 크기를 {new_scale}로 늘립니다.")
    print() 
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={new_scale}", "--build"],
            check=True
        )
    except Exception as e:
        print(f"Error while scaling out: {e}")

def scale_in(current_scale):
    new_scale = max(1, current_scale - 1)  # 현재 스케일에서 1 감소, 최소 1 유지
    print() 
    print("Scale in...") 
    print(f"Scale 크기를 {new_scale}로 줄입니다.")
    print() 
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={new_scale}", "--build"],
            check=True
        )
    except Exception as e:
        print(f"Error while scaling in: {e}")

def monitor_docker():
    """Docker 컨테이너를 모니터링하고 스케일을 조정합니다."""
    current_scale = 1 
    while True:
        stats = get_docker_stats(target_container_name)
        if stats:
            cpu_usage = float(stats['CPUPerc'].replace('%', ''))
            
            print() 
            print(f"현재 {target_container_name}의 CPU는 {cpu_usage}%입니다.")
            print()
            if cpu_usage > cpu_scale_out:
                scale_out(current_scale)  # CPU 사용량이 임계값을 초과하면 스케일 아웃
                current_scale += 1  # 현재 스케일 증가
            elif cpu_usage < cpu_scale_in:
                scale_in(current_scale)  # CPU 사용량이 임계값 이하일 경우 스케일 인
                current_scale = max(1, current_scale - 1)  # 현재 스케일 감소, 최소 1 유지

#        time.sleep(check_interval)  # 체크 간격만큼 대기

if __name__ == "__main__":
    monitor_docker()






