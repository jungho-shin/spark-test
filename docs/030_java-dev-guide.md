# Java 개발환경 구축 가이드

## 목차
1. [JDK 설치](#1-jdk-설치)
2. [환경변수 설정](#2-환경변수-설정)
3. [빌드 도구 설치](#3-빌드-도구-설치)
4. [IDE 설치 및 설정](#4-ide-설치-및-설정)
5. [개발환경 검증](#5-개발환경-검증)
6. [추가 도구](#6-추가-도구)

---

## 1. JDK 설치

### Ubuntu / Debian

```bash
# 패키지 목록 업데이트
sudo apt update

# OpenJDK 17 설치 (LTS 권장)
sudo apt install -y openjdk-17-jdk

# 또는 OpenJDK 21 설치 (최신 LTS)
sudo apt install -y openjdk-21-jdk

# 설치 확인
java -version
javac -version
```

### 여러 버전 관리 (Ubuntu)

```bash
# 설치된 Java 목록 확인
sudo update-alternatives --list java

# 기본 버전 변경
sudo update-alternatives --config java
sudo update-alternatives --config javac
```

### macOS

```bash
# Homebrew를 이용한 설치
brew install openjdk@17

# 또는 SDKMAN 이용 (버전 관리 편리)
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh

sdk install java 17.0.9-tem
sdk install java 21.0.1-tem

# 버전 전환
sdk use java 17.0.9-tem
```

### Windows

1. [OpenJDK 다운로드](https://adoptium.net/) 또는 [Oracle JDK 다운로드](https://www.oracle.com/java/technologies/downloads/)
2. 설치 파일 실행 후 안내에 따라 설치
3. 환경변수 설정 (아래 참고)

---

## 2. 환경변수 설정

### Linux / macOS

```bash
# ~/.bashrc 또는 ~/.zshrc 에 추가
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH=$JAVA_HOME/bin:$PATH
```

```bash
# 적용
source ~/.bashrc   # bash 사용 시
source ~/.zshrc    # zsh 사용 시

# 확인
echo $JAVA_HOME
java -version
```

### macOS (Homebrew 설치 시)

```bash
# ~/.zshrc 에 추가
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export PATH=$JAVA_HOME/bin:$PATH
```

### Windows

1. **시스템 속성** → **고급** → **환경 변수** 클릭
2. **시스템 변수**에서 **새로 만들기**
   - 변수 이름: `JAVA_HOME`
   - 변수 값: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x.x-hotspot`
3. **Path** 변수 편집 → `%JAVA_HOME%\bin` 추가
4. 명령 프롬프트 재시작 후 확인:

```cmd
java -version
javac -version
echo %JAVA_HOME%
```

---

## 3. 빌드 도구 설치

### Maven

```bash
# Ubuntu
sudo apt install -y maven

# macOS
brew install maven

# 버전 확인
mvn -version
```

`~/.m2/settings.xml` (선택적 설정):

```xml
<settings>
  <mirrors>
    <mirror>
      <id>central</id>
      <mirrorOf>central</mirrorOf>
      <url>https://repo1.maven.org/maven2</url>
    </mirror>
  </mirrors>
</settings>
```

### Gradle

```bash
# Ubuntu
sudo apt install -y gradle

# macOS
brew install gradle

# SDKMAN 이용 (버전 관리 편리)
sdk install gradle 8.5

# 버전 확인
gradle -version
```

### Gradle Wrapper 사용 (프로젝트 내)

```bash
# 새 프로젝트에 Wrapper 생성
gradle wrapper --gradle-version 8.5

# 이후 직접 gradle 명령 대신 wrapper 사용
./gradlew build      # Linux/macOS
gradlew.bat build    # Windows
```

---

## 4. IDE 설치 및 설정

### IntelliJ IDEA (권장)

1. [JetBrains 다운로드](https://www.jetbrains.com/idea/download/) 에서 설치
   - **Community Edition**: 무료, Java/Kotlin 개발 가능
   - **Ultimate Edition**: 유료, Spring/웹 개발 포함

2. **JDK 설정**
   - `File` → `Project Structure` → `SDKs` → `+` → `Add JDK`
   - JAVA_HOME 경로 입력

3. **권장 플러그인**

| 플러그인 | 용도 |
|---|---|
| Lombok | 보일러플레이트 코드 자동 생성 |
| SonarLint | 코드 품질 분석 |
| GitToolBox | Git 통합 강화 |
| Rainbow Brackets | 괄호 색상 구분 |
| Key Promoter X | 단축키 학습 |

### VS Code

```bash
# Extensions 설치
code --install-extension vscjava.vscode-java-pack
code --install-extension vscjava.vscode-spring-initializr
code --install-extension redhat.java
```

`settings.json` 설정:

```json
{
  "java.home": "/usr/lib/jvm/java-17-openjdk-amd64",
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-17",
      "path": "/usr/lib/jvm/java-17-openjdk-amd64",
      "default": true
    }
  ]
}
```

---

## 5. 개발환경 검증

### Hello World 테스트

```bash
# 작업 디렉토리 생성
mkdir hello-java && cd hello-java
```

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
        System.out.println("Java version: " + System.getProperty("java.version"));
        System.out.println("JAVA_HOME: " + System.getenv("JAVA_HOME"));
    }
}
```

```bash
# 컴파일 및 실행
javac HelloWorld.java
java HelloWorld
```

### Maven 프로젝트 생성 테스트

```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-app \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DarchetypeVersion=1.4 \
  -DinteractiveMode=false

cd my-app
mvn package
java -cp target/my-app-1.0-SNAPSHOT.jar com.example.App
```

### Gradle 프로젝트 생성 테스트

```bash
mkdir my-gradle-app && cd my-gradle-app
gradle init --type java-application --dsl groovy

./gradlew run
```

---

## 6. 추가 도구

### Docker (컨테이너 기반 개발)

```bash
# Ubuntu
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

# 확인
docker --version
```

### Git

```bash
# Ubuntu
sudo apt install -y git

# 초기 설정
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global core.editor "vim"
```

### 자주 쓰는 JVM 옵션

```bash
# 힙 메모리 설정
java -Xms512m -Xmx2g -jar app.jar

# GC 로그 출력
java -Xlog:gc* -jar app.jar

# 원격 디버깅 (포트 5005)
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 -jar app.jar
```

### Java 버전별 주요 특징

| 버전 | 출시 | 주요 특징 |
|---|---|---|
| Java 8 (LTS) | 2014 | Lambda, Stream API, Optional |
| Java 11 (LTS) | 2018 | var 키워드, HTTP Client API |
| Java 17 (LTS) | 2021 | Sealed Classes, Pattern Matching |
| Java 21 (LTS) | 2023 | Virtual Threads, Record Patterns |

---

## 빠른 설치 스크립트 (Ubuntu)

```bash
#!/bin/bash
set -e

echo "=== Java 개발환경 자동 설치 ==="

# JDK 17 설치
sudo apt update
sudo apt install -y openjdk-17-jdk maven

# JAVA_HOME 설정
JAVA_HOME_PATH=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_HOME_PATH" >> ~/.bashrc
echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# Gradle 설치
curl -s "https://get.sdkman.io" | bash
source ~/.sdkman/bin/sdkman-init.sh
sdk install gradle 8.5

echo "=== 설치 완료 ==="
java -version
mvn -version
gradle -version
```

---

> **참고 링크**
> - [OpenJDK 공식 사이트](https://openjdk.org/)
> - [Eclipse Adoptium (Temurin JDK)](https://adoptium.net/)
> - [Maven 공식 문서](https://maven.apache.org/guides/)
> - [Gradle 공식 문서](https://docs.gradle.org/)
> - [IntelliJ IDEA 문서](https://www.jetbrains.com/help/idea/)
