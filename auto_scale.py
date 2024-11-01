import subprocess
import json
import time
from datetime import datetime
import requests
from scale_config import cpu_scale_out, cpu_scale_in, check_interval, scale_out_duration, line_notify_token

target_container_name = 'samdul-blog-1'
log_file = "scale_log.txt"

def send_line_notification(message):
    """LINE Notify로 알림을 보냅니다."""
    headers = {
        "Authorization": f"Bearer {line_notify_token}"
    }
    data = {
        "message": message
    }
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
    if response.status_code == 200:
        print("LINE 알림이 성공적으로 전송되었습니다.")
    else:
        print("LINE 알림 전송에 실패했습니다.")

def get_docker_stats(container_name):
    try:
        r = subprocess.check_output(
            ["docker", "stats", "samdul-blog-1", "--no-stream", "--format", "{{json .}}"],
            text=True
        )
        return json.loads(r)
    except subprocess.CalledProcessError as e:
        print(f"Error while getting stats for {container_name}: {e}")
        return None

def log_event(event):
    """로그 파일에 이벤트를 기록합니다."""
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {event}\n")

def scale_out(current_scale):
    new_scale = current_scale + 1
    print("\nScale out...")
    print(f"Scale 크기를 {new_scale}로 늘립니다.\n")
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={new_scale}", "--build"],
            check=True
        )
        log_event(f"Scale out to {new_scale}")
        send_line_notification(f"🚀 Scale Out 실행: 스케일이 {new_scale}로 증가했습니다.")
    except Exception as e:
        print(f"Error while scaling out: {e}")

def scale_in(current_scale):
    new_scale = max(1, current_scale - 1)
    print("\nScale in...")
    print(f"Scale 크기를 {new_scale}로 줄입니다.\n")
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={new_scale}", "--build"],
            check=True
        )
        log_event(f"Scale in to {new_scale}")
        send_line_notification(f"📉 Scale In 실행: 스케일이 {new_scale}로 감소했습니다.")
    except Exception as e:
        print(f"Error while scaling in: {e}")

def monitor_docker():
    current_scale = 1
    scale_out_start_time = None

    while True:
        stats = get_docker_stats(target_container_name)
        if stats:
            cpu_usage = float(stats['CPUPerc'].replace('%', ''))

            print(f"\n현재 {target_container_name}의 CPU는 {cpu_usage}%입니다.\n")

            if cpu_usage > cpu_scale_out:
                if scale_out_start_time is None:
                    scale_out_start_time = time.time()
                elif time.time() - scale_out_start_time >= scale_out_duration:
                    scale_out(current_scale)
                    current_scale += 1
                    scale_out_start_time = None
            else:
                scale_out_start_time = None  # 임계값 미만으로 떨어지면 초기화

            if cpu_usage < cpu_scale_in:
                scale_in(current_scale)
                current_scale = max(1, current_scale - 1)

        time.sleep(check_interval)

if __name__ == "__main__":
    monitor_docker()

