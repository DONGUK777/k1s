import subprocess
import json
import time
from scale_config import cpu_scale_out, cpu_scale_in, check_interval, scale_out_duration  # config 파일에서 값 가져오기

# 기본 설정값
target_container_name = 'samdul-blog-1'

def get_docker_stats(container_name):
    """특정 Docker 컨테이너의 통계 정보를 가져옵니다."""
    try:
        r = subprocess.check_output(
            ["docker", "stats", "samdul-blog-1", "--no-stream", "--format", "{{json .}}"],
            text=True
        )
        return json.loads(r)
    except subprocess.CalledProcessError as e:
        print(f"Error while getting stats for {container_name}: {e}")
        return None

def scale_out(current_scale):
    new_scale = current_scale + 1  # 현재 스케일에서 1 증가
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
    cpu_exceed_start_time = None  # CPU 임계값 초과 시작 시간
    
    while True:
        stats = get_docker_stats(target_container_name)
        if stats:
            cpu_usage = float(stats['CPUPerc'].replace('%', ''))

            print(f"현재 {target_container_name}의 CPU는 {cpu_usage}%입니다.")
            print()

            # 스케일 아웃 조건
            if cpu_usage > cpu_scale_out:
                if cpu_exceed_start_time is None:
                    # 초과 시작 시간 기록
                    cpu_exceed_start_time = time.time()
                elif (time.time() - cpu_exceed_start_time) >= scale_out_duration:
                    # 지속 시간 초과 시 스케일 아웃
                    scale_out(current_scale)
                    current_scale += 1  # 현재 스케일 증가
                    cpu_exceed_start_time = None  # 초기화
            else:
                # 스케일 인 조건
                cpu_exceed_start_time = None  # CPU 사용량이 임계값 이하일 경우 초기화
                if cpu_usage < cpu_scale_in:
                    scale_in(current_scale)
                    current_scale = max(1, current_scale - 1)  # 현재 스케일 감소, 최소 1 유지

        time.sleep(check_interval)  # 체크 간격만큼 대기

if __name__ == "__main__":
    monitor_docker()


