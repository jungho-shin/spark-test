# 최종 해결 단계: 키 포맷 변환 및 저장소 재등록



# 1. 기존 패키지 제거 (있다면)

```Bash
sudo rm /etc/apt/keyrings/docker.gpg
sudo rm /etc/apt/sources.list.d/docker.list
```



# 2. 필수 패키지 설치

```Bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```



# 3. Docker 공식 GPG 키 추가
(단순 다운로드가 아니라 gpg --dearmor를 통해 apt가 즉시 인식할 수 있는 바이너리 포맷으로 변환합니다.)

```Bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```



# 4. Docker 저장소 등록

```Bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```



# 5. Docker Engine + Compose 플러그인 설치

```Bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
---

## 그래도 안 된다면?
(최후의 수단: --keyring 경로 무시)
위의 방법으로도 NO_PUBKEY 에러가 계속된다면, 시스템의 메인 키링에 강제로 등록하는 방법이 있습니다.

```Bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8
sudo apt update
```
(참고: apt-key는 최신 우분투에서 권장되지 않는(deprecated) 방식이지만, 경로 문제로 인한 에러를 해결하는 데는 매우 강력한 효과가 있습니다.)

---

# 6. 설치 확인

```Bash
docker --version
docker compose version
sudo docker run hello-world
```



# 7. sudo 없이 docker 사용 (선택)

```Bash
sudo usermod -aG docker $USER
newgrp docker
```
로그아웃 후 재로그인하면 적용됩니다.



# 8. 부팅 시 자동 시작

```Bash
sudo systemctl enable docker
sudo systemctl start docker
```