import subprocess
import json
import time
from datetime import datetime
from scale_config import cpu_scale_out, cpu_scale_in, check_interval, scale_out_duration  # 설정값 가져오기

# 기본 설정값
target_container_name = 'samdul-load_balancer-1'
#log_file = "scale_log.txt"  # 로그 파일 경로
#
#def log_scale_action(action, new_scale):
#    """스케일 인/아웃 동작을 로그 파일에 기록합니다."""
#    with open(log_file, "a") as f:
#        log_entry = f"{datetime.now()} - {action} to scale {new_scale}\n"
#        f.write(log_entry)

def get_docker_stats(container_name):
    """특정 Docker 컨테이너의 통계 정보를 가져옵니다."""
    try:
        r = subprocess.check_output(
            ["docker", "stats", container_name, "--no-stream", "--format", "{{json .}}"],
            text=True
        )
        return json.loads(r)
    except subprocess.CalledProcessError as e:
        print(f"Error while getting stats for {container_name}: {e}")
        return None

def scale_out(current_scale):
    new_scale = current_scale + 1
    print("Scale out...")
    print(f"Scale 크기를 {new_scale}로 늘립니다.")
    print()
#    log_scale_action("Scale out", new_scale)  # 스케일 아웃 로그 기록
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={new_scale}", "--build"],
            check=True
        )
    except Exception as e:
        print(f"Error while scaling out: {e}")

def scale_in(current_scale):
    new_scale = max(1, current_scale - 1)
    print("Scale in...")
    print(f"Scale 크기를 {new_scale}로 줄입니다.")
    print()
#    log_scale_action("Scale in", new_scale)  # 스케일 인 로그 기록
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
    cpu_exceed_start_time = None
    
    while True:
        stats = get_docker_stats(target_container_name)
        if stats:
            cpu_usage = float(stats['CPUPerc'].replace('%', ''))

            print()
            print(f"현재 {target_container_name}의 CPU는 {cpu_usage}%입니다.")
            print()

            if cpu_usage > cpu_scale_out:
                if cpu_exceed_start_time is None:
                    cpu_exceed_start_time = time.time()
                elif (time.time() - cpu_exceed_start_time) >= scale_out_duration:
                    scale_out(current_scale)
                    current_scale += 1
                    cpu_exceed_start_time = None
            else:
                cpu_exceed_start_time = None
                if cpu_usage < cpu_scale_in:
                    scale_in(current_scale)
                    current_scale = max(1, current_scale - 1)

        time.sleep(check_interval)

if __name__ == "__main__":
    monitor_docker()

