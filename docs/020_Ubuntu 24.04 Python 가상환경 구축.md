# Ubuntu 24.04에서 Python 가상환경 구축



# 1. 필요한 패키지 설치

```Bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```



# 2. 가상환경 생성

```Bash
python3 -m venv venv
```



# 3. 가상환경 활성화

```Bash
source venv/bin/activate
```



# 4. 패키지 설치

```Bash
pip install -r requirement.txt
```
